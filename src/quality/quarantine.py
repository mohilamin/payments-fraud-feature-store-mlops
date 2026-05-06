from __future__ import annotations

import pandas as pd

from src.common.config import get_path
from src.common.paths import ensure_directory


def write_quality_outputs(transactions: pd.DataFrame, issues: pd.DataFrame) -> None:
    """Write issue report and quarantined transaction records."""
    processed = ensure_directory(get_path("processed"))
    quarantine = ensure_directory(processed / "quarantine")
    issues.to_csv(processed / "data_quality_issues.csv", index=False)
    if issues.empty:
        pd.DataFrame().to_csv(quarantine / "payment_transactions_quarantine.csv", index=False)
        return
    bad_ids = set(issues["record_id"])
    transactions.loc[transactions["transaction_id"].isin(bad_ids)].to_csv(
        quarantine / "payment_transactions_quarantine.csv",
        index=False,
    )
