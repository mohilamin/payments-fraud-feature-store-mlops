from __future__ import annotations

import pandas as pd

from src.features.velocity_features import prior_window_count, prior_window_sum


def build_customer_features(transactions: pd.DataFrame) -> pd.DataFrame:
    """Build point-in-time customer features."""
    frame = transactions.copy()
    frame["customer_txn_count_1h"] = prior_window_count(frame, "customer_id", "1h")
    frame["customer_txn_count_24h"] = prior_window_count(frame, "customer_id", "24h")
    frame["customer_total_amount_24h"] = prior_window_sum(frame, "customer_id", "amount", "24h")
    frame["customer_avg_amount_30d"] = _prior_mean(frame, "customer_id", "amount", "30d")
    frame["customer_failed_auth_count_24h"] = _prior_failed_auth(frame)
    frame["customer_distinct_merchants_24h"] = _prior_nunique(frame, "customer_id", "merchant_id", "24h")
    frame["customer_distinct_countries_24h"] = _prior_nunique(frame, "customer_id", "merchant_country", "24h")
    return frame[
        [
            "transaction_id",
            "customer_txn_count_1h",
            "customer_txn_count_24h",
            "customer_total_amount_24h",
            "customer_avg_amount_30d",
            "customer_failed_auth_count_24h",
            "customer_distinct_merchants_24h",
            "customer_distinct_countries_24h",
        ]
    ]


def _prior_mean(frame: pd.DataFrame, entity: str, value: str, window: str) -> pd.Series:
    sums = prior_window_sum(frame, entity, value, window)
    counts = prior_window_count(frame, entity, window).replace(0, pd.NA)
    return (sums / counts).fillna(frame[value].median())


def _prior_failed_auth(frame: pd.DataFrame) -> pd.Series:
    temp = frame.copy()
    temp["failed"] = (temp["auth_result"] == "declined").astype(int)
    return prior_window_sum(temp, "customer_id", "failed", "24h")


def _prior_nunique(frame: pd.DataFrame, entity: str, col: str, window: str) -> pd.Series:
    values = pd.Series(0.0, index=frame.index)
    delta = pd.Timedelta(window)
    for _, group in frame.groupby(entity, sort=False):
        ordered = group.sort_values("transaction_timestamp")
        for idx, row in ordered.iterrows():
            start = row["transaction_timestamp"] - delta
            mask = (ordered["transaction_timestamp"] < row["transaction_timestamp"]) & (
                ordered["transaction_timestamp"] >= start
            )
            values.loc[idx] = ordered.loc[mask, col].nunique()
    return values
