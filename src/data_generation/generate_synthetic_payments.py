from __future__ import annotations

import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.common.config import get_path, get_settings
from src.common.logging import get_logger
from src.common.paths import ensure_directory

LOGGER = get_logger(__name__)

COUNTRIES = ["US", "CA", "GB", "MX", "FR", "DE"]
CURRENCIES = ["USD", "CAD", "GBP", "MXN", "EUR"]
CATEGORIES = ["grocery", "fuel", "travel", "electronics", "gaming", "jewelry", "crypto"]
CHANNELS = ["card_present", "card_not_present", "wallet", "bank_transfer"]


def generate_synthetic_payments() -> None:
    """Generate deterministic synthetic payment data and injected issue manifests."""
    rng = np.random.default_rng(int(get_settings()["random_seed"]))
    raw = ensure_directory(get_path("raw"))

    customers = _customers(rng)
    accounts = _accounts(rng, customers)
    merchants = _merchants(rng)
    devices = _devices(rng, customers)
    merchant_profiles = _merchant_profiles(rng, merchants)
    device_profiles = _device_profiles(rng, devices)
    transactions = _transactions(rng, customers, accounts, merchants, devices)
    transactions, fraud_manifest = _inject_fraud_patterns(transactions, rng, merchants)
    transactions, quality_manifest = _inject_quality_issues(transactions, accounts, rng)
    chargebacks = _chargebacks(transactions)
    fraud_labels = transactions[["transaction_id", "fraud_label"]].copy()

    outputs = {
        "customers.csv": customers,
        "accounts.csv": accounts,
        "merchants.csv": merchants,
        "devices.csv": devices,
        "payment_transactions.csv": transactions,
        "chargebacks.csv": chargebacks,
        "fraud_labels.csv": fraud_labels,
        "merchant_risk_profiles.csv": merchant_profiles,
        "device_risk_profiles.csv": device_profiles,
    }
    for filename, frame in outputs.items():
        frame.to_csv(raw / filename, index=False)
    (raw / "injected_fraud_pattern_manifest.json").write_text(
        json.dumps(fraud_manifest, indent=2),
        encoding="utf-8",
    )
    (raw / "injected_data_quality_manifest.json").write_text(
        json.dumps(quality_manifest, indent=2),
        encoding="utf-8",
    )
    LOGGER.info("synthetic payment data generated", extra={"transactions": len(transactions)})


def _customers(rng: np.random.Generator) -> pd.DataFrame:
    count = 2000
    created = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 700, count), unit="D")
    return pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(count)],
            "customer_segment": rng.choice(["retail", "small_business", "premium"], count),
            "customer_country": rng.choice(COUNTRIES, count, p=[0.72, 0.08, 0.06, 0.06, 0.04, 0.04]),
            "customer_since": created.astype(str),
            "kyc_status": rng.choice(["verified", "review", "restricted"], count, p=[0.94, 0.05, 0.01]),
        }
    )


def _accounts(rng: np.random.Generator, customers: pd.DataFrame) -> pd.DataFrame:
    count = 2500
    customer_ids = rng.choice(customers["customer_id"], count)
    return pd.DataFrame(
        {
            "account_id": [f"A{i:05d}" for i in range(count)],
            "customer_id": customer_ids,
            "account_type": rng.choice(["checking", "credit", "wallet"], count),
            "account_open_date": "2024-01-01",
            "account_status": rng.choice(["open", "closed"], count, p=[0.96, 0.04]),
        }
    )


def _merchants(rng: np.random.Generator) -> pd.DataFrame:
    count = 1000
    return pd.DataFrame(
        {
            "merchant_id": [f"M{i:05d}" for i in range(count)],
            "merchant_category": rng.choice(CATEGORIES, count),
            "merchant_country": rng.choice(COUNTRIES, count, p=[0.65, 0.08, 0.08, 0.08, 0.06, 0.05]),
            "merchant_status": rng.choice(["active", "watchlist"], count, p=[0.92, 0.08]),
        }
    )


def _devices(rng: np.random.Generator, customers: pd.DataFrame) -> pd.DataFrame:
    count = 3000
    first_seen = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 420, count), unit="D")
    return pd.DataFrame(
        {
            "device_id": [f"D{i:05d}" for i in range(count)],
            "customer_id": rng.choice(customers["customer_id"], count),
            "device_fingerprint": [f"fp_{i:05d}" for i in range(count)],
            "device_type": rng.choice(["ios", "android", "web"], count),
            "first_seen_at": first_seen.astype(str),
        }
    )


def _merchant_profiles(rng: np.random.Generator, merchants: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "merchant_id": merchants["merchant_id"],
            "merchant_risk_score": np.round(rng.beta(2, 8, len(merchants)), 4),
            "chargeback_rate_baseline": np.round(rng.beta(1, 30, len(merchants)), 4),
        }
    )


def _device_profiles(rng: np.random.Generator, devices: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "device_id": devices["device_id"],
            "device_risk_score": np.round(rng.beta(2, 10, len(devices)), 4),
        }
    )


def _transactions(
    rng: np.random.Generator,
    customers: pd.DataFrame,
    accounts: pd.DataFrame,
    merchants: pd.DataFrame,
    devices: pd.DataFrame,
) -> pd.DataFrame:
    count = 50000
    account_rows = accounts.sample(count, replace=True, random_state=42).reset_index(drop=True)
    merchant_rows = merchants.sample(count, replace=True, random_state=7).reset_index(drop=True)
    device_rows = devices.sample(count, replace=True, random_state=11).reset_index(drop=True)
    customer_country = customers.set_index("customer_id")["customer_country"]
    start = datetime(2025, 1, 1)
    timestamps = [start + timedelta(minutes=int(x)) for x in rng.integers(0, 60 * 24 * 90, count)]
    amount = np.round(rng.lognormal(mean=3.2, sigma=0.85, size=count), 2)
    auth = rng.choice(["approved", "declined"], count, p=[0.94, 0.06])
    frame = pd.DataFrame(
        {
            "transaction_id": [f"T{i:07d}" for i in range(count)],
            "customer_id": account_rows["customer_id"],
            "account_id": account_rows["account_id"],
            "merchant_id": merchant_rows["merchant_id"],
            "device_id": device_rows["device_id"],
            "transaction_timestamp": [ts.isoformat() for ts in timestamps],
            "amount": amount,
            "currency": rng.choice(CURRENCIES, count, p=[0.78, 0.06, 0.05, 0.05, 0.06]),
            "payment_channel": rng.choice(CHANNELS, count, p=[0.45, 0.35, 0.15, 0.05]),
            "merchant_category": merchant_rows["merchant_category"],
            "merchant_country": merchant_rows["merchant_country"],
            "customer_country": account_rows["customer_id"].map(customer_country),
            "card_present_flag": 0,
            "auth_result": auth,
            "ip_country": rng.choice(COUNTRIES, count),
            "device_fingerprint": device_rows["device_fingerprint"],
            "transaction_status": np.where(auth == "approved", "settled", "declined"),
            "fraud_label": 0,
        }
    )
    frame["card_present_flag"] = (frame["payment_channel"] == "card_present").astype(int)
    frame["is_international"] = (frame["merchant_country"] != frame["customer_country"]).astype(int)
    return frame.sort_values("transaction_timestamp").reset_index(drop=True)


def _inject_fraud_patterns(
    transactions: pd.DataFrame,
    rng: np.random.Generator,
    merchants: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = transactions.copy()
    manifest: dict[str, object] = {"patterns": []}
    pattern_names = [
        "high_velocity_transactions",
        "impossible_travel",
        "new_device_high_value_purchase",
        "merchant_risk_spike",
        "international_transaction_mismatch",
        "repeated_declines_then_approval",
        "account_takeover_pattern",
        "unusual_merchant_category",
        "amount_outlier",
        "night_time_transaction_burst",
        "card_not_present_fraud",
        "synthetic_chargeback_pattern",
    ]
    for index, pattern in enumerate(pattern_names):
        rows = rng.choice(frame.index, 180, replace=False)
        frame.loc[rows, "fraud_label"] = 1
        if "high_velocity" in pattern:
            customer = frame.loc[rows[0], "customer_id"]
            base_time = pd.Timestamp(frame.loc[rows[0], "transaction_timestamp"])
            frame.loc[rows, "customer_id"] = customer
            frame.loc[rows, "transaction_timestamp"] = [
                (base_time + timedelta(minutes=i % 25)).isoformat() for i in range(len(rows))
            ]
        if "international" in pattern or "impossible" in pattern:
            frame.loc[rows, "merchant_country"] = "GB"
            frame.loc[rows, "customer_country"] = "US"
            frame.loc[rows, "ip_country"] = "DE"
            frame.loc[rows, "is_international"] = 1
        if "new_device" in pattern:
            frame.loc[rows, "amount"] = frame.loc[rows, "amount"] * 15 + 500
        if "merchant_risk" in pattern:
            risky_merchant = merchants.iloc[index]["merchant_id"]
            frame.loc[rows, "merchant_id"] = risky_merchant
        if "declines" in pattern:
            frame.loc[rows[:-20], "auth_result"] = "declined"
            frame.loc[rows[:-20], "transaction_status"] = "declined"
            frame.loc[rows[-20:], "auth_result"] = "approved"
            frame.loc[rows[-20:], "transaction_status"] = "settled"
        if "category" in pattern:
            frame.loc[rows, "merchant_category"] = rng.choice(["crypto", "gaming", "jewelry"], len(rows))
        if "outlier" in pattern:
            frame.loc[rows, "amount"] = frame.loc[rows, "amount"] * 25 + 1000
        if "night" in pattern:
            dates = pd.to_datetime(frame.loc[rows, "transaction_timestamp"])
            frame.loc[rows, "transaction_timestamp"] = [
                dt.replace(hour=2, minute=int(i % 60)).isoformat() for i, dt in enumerate(dates)
            ]
        if "card_not_present" in pattern:
            frame.loc[rows, "payment_channel"] = "card_not_present"
            frame.loc[rows, "card_present_flag"] = 0
        manifest["patterns"].append(
            {
                "pattern_type": pattern,
                "transaction_ids": frame.loc[rows, "transaction_id"].tolist(),
                "expected_fraud_count": int(len(rows)),
                "metadata": {
                    "synthetic_only": True,
                    "injection_batch": index + 1,
                    "primary_signal": pattern,
                },
            }
        )
    return frame.sort_values("transaction_timestamp").reset_index(drop=True), manifest


def _inject_quality_issues(
    transactions: pd.DataFrame,
    accounts: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = transactions.copy()
    manifest: dict[str, object] = {"issues": []}
    specs = [
        ("missing_customer_id", "customer_id", ""),
        ("invalid_merchant_id", "merchant_id", "M99999"),
        ("invalid_device_id", "device_id", "D99999"),
        ("negative_transaction_amount", "amount", -25.0),
        ("future_transaction_timestamp", "transaction_timestamp", "2035-01-01T00:00:00"),
        ("invalid_currency", "currency", "ZZZ"),
        ("missing_fraud_label", "fraud_label", np.nan),
        ("inconsistent_country_codes", "customer_country", "USA"),
    ]
    for issue_type, column, value in specs:
        rows = rng.choice(frame.index, 20, replace=False)
        frame.loc[rows, column] = value
        manifest["issues"].append(
            {
                "issue_type": issue_type,
                "transaction_ids": frame.loc[rows, "transaction_id"].tolist(),
                "expected_count": int(len(rows)),
            }
        )
    duplicate_rows = frame.sample(20, random_state=99)
    frame = pd.concat([frame, duplicate_rows], ignore_index=True)
    manifest["issues"].append(
        {
            "issue_type": "duplicate_transactions",
            "transaction_ids": duplicate_rows["transaction_id"].tolist(),
            "expected_count": int(len(duplicate_rows)),
        }
    )
    closed_accounts = accounts.loc[accounts["account_status"] == "closed", "account_id"].head(20)
    rows = rng.choice(frame.index, len(closed_accounts), replace=False)
    frame.loc[rows, "account_id"] = closed_accounts.to_numpy()
    manifest["issues"].append(
        {
            "issue_type": "closed_account_transactions",
            "transaction_ids": frame.loc[rows, "transaction_id"].tolist(),
            "expected_count": int(len(rows)),
        }
    )
    return frame, manifest


def _chargebacks(transactions: pd.DataFrame) -> pd.DataFrame:
    fraud = transactions.loc[transactions["fraud_label"].fillna(0).astype(float).eq(1)].head(600)
    return pd.DataFrame(
        {
            "chargeback_id": [f"CB{i:06d}" for i in range(len(fraud))],
            "transaction_id": fraud["transaction_id"].to_numpy(),
            "chargeback_timestamp": (
                pd.to_datetime(fraud["transaction_timestamp"], errors="coerce") + pd.Timedelta(days=7)
            ).astype(str),
            "chargeback_reason": "synthetic_fraud_dispute",
        }
    )


if __name__ == "__main__":
    generate_synthetic_payments()
