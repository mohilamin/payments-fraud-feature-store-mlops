from __future__ import annotations

import pandas as pd

from src.features.velocity_features import prior_window_count, prior_window_sum


def build_merchant_features(transactions: pd.DataFrame, merchant_profiles: pd.DataFrame, chargebacks: pd.DataFrame) -> pd.DataFrame:
    """Build point-in-time merchant features."""
    frame = transactions.copy()
    frame["merchant_txn_count_24h"] = prior_window_count(frame, "merchant_id", "24h")
    frame["merchant_avg_amount_30d"] = (
        prior_window_sum(frame, "merchant_id", "amount", "30D")
        / prior_window_count(frame, "merchant_id", "30D").mask(lambda series: series == 0)
    ).fillna(frame["amount"].median())
    frame["merchant_fraud_rate_30d"] = _prior_rate(frame, "merchant_id", "fraud_label", "30D")
    cb_ids = set(chargebacks["transaction_id"].astype(str))
    frame["chargeback"] = frame["transaction_id"].isin(cb_ids).astype(int)
    frame["merchant_chargeback_rate_30d"] = _prior_rate(frame, "merchant_id", "chargeback", "30D")
    frame = frame.merge(merchant_profiles, on="merchant_id", how="left")
    return frame[
        [
            "transaction_id",
            "merchant_txn_count_24h",
            "merchant_fraud_rate_30d",
            "merchant_avg_amount_30d",
            "merchant_chargeback_rate_30d",
            "merchant_risk_score",
        ]
    ]


def _prior_rate(frame: pd.DataFrame, entity: str, col: str, window: str) -> pd.Series:
    sums = prior_window_sum(frame, entity, col, window)
    counts = prior_window_count(frame, entity, window).mask(lambda series: series == 0)
    return (sums / counts).fillna(0)
