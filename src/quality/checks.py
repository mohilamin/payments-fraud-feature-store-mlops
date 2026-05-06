from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from src.quality.rules import VALID_COUNTRIES, VALID_CURRENCIES


def detect_quality_issues(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Detect transaction-level data quality issues."""
    txns = frames["payment_transactions"].copy()
    merchants = set(frames["merchants"]["merchant_id"].astype(str))
    devices = set(frames["devices"]["device_id"].astype(str))
    accounts = frames["accounts"].set_index("account_id")["account_status"].to_dict()
    issues: list[dict[str, object]] = []

    def add(mask: pd.Series, column: str, issue_type: str, severity: str, action: str) -> None:
        for _, row in txns.loc[mask].iterrows():
            issues.append(
                {
                    "issue_id": f"DQ-{len(issues) + 1:06d}",
                    "table_name": "payment_transactions",
                    "record_id": row["transaction_id"],
                    "column_name": column,
                    "issue_type": issue_type,
                    "severity": severity,
                    "description": f"{issue_type} detected for transaction {row['transaction_id']}",
                    "recommended_action": action,
                    "detected_at": datetime.now(UTC).isoformat(),
                }
            )

    add(txns.duplicated("transaction_id", keep=False), "transaction_id", "duplicate_transactions", "high", "quarantine_duplicate")
    add(txns["customer_id"].astype(str).eq(""), "customer_id", "missing_customer_id", "critical", "quarantine_record")
    add(~txns["merchant_id"].astype(str).isin(merchants), "merchant_id", "invalid_merchant_id", "critical", "fix_reference_data")
    add(~txns["device_id"].astype(str).isin(devices), "device_id", "invalid_device_id", "high", "fix_reference_data")
    add(pd.to_numeric(txns["amount"], errors="coerce").lt(0), "amount", "negative_transaction_amount", "high", "quarantine_record")
    add(pd.to_datetime(txns["transaction_timestamp"], errors="coerce").gt(pd.Timestamp("2026-05-06")), "transaction_timestamp", "future_transaction_timestamp", "high", "quarantine_record")
    add(~txns["currency"].astype(str).isin(VALID_CURRENCIES), "currency", "invalid_currency", "medium", "standardize_currency")
    add(txns["fraud_label"].astype(str).eq(""), "fraud_label", "missing_fraud_label", "critical", "exclude_from_training")
    add(~txns["customer_country"].astype(str).isin(VALID_COUNTRIES), "customer_country", "inconsistent_country_codes", "medium", "standardize_country_code")
    closed = txns["account_id"].map(accounts).eq("closed")
    add(closed, "account_id", "transactions_linked_to_closed_accounts", "critical", "quarantine_record")
    return pd.DataFrame(issues)


def clean_transactions(frames: dict[str, pd.DataFrame], issues: pd.DataFrame) -> pd.DataFrame:
    """Return transactions after excluding critical quality issues."""
    txns = frames["payment_transactions"].copy()
    if issues.empty:
        return txns
    bad_ids = set(issues.loc[issues["severity"].isin(["critical", "high"]), "record_id"])
    return txns.loc[~txns["transaction_id"].isin(bad_ids)].drop_duplicates("transaction_id").copy()
