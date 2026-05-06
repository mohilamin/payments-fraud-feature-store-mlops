from __future__ import annotations

import pandas as pd

from src.features.velocity_features import prior_window_count


def build_device_features(transactions: pd.DataFrame, devices: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
    """Build point-in-time device features."""
    frame = transactions.copy()
    frame["device_txn_count_24h"] = prior_window_count(frame, "device_id", "24h")
    frame["device_distinct_customers_24h"] = _prior_device_customers(frame)
    first_seen = devices.set_index("device_id")["first_seen_at"].pipe(pd.to_datetime)
    frame["device_age_days"] = (
        frame["transaction_timestamp"] - frame["device_id"].map(first_seen)
    ).dt.days.clip(lower=0)
    frame = frame.merge(profiles, on="device_id", how="left")
    first_customer_device = frame.groupby(["customer_id", "device_id"])["transaction_timestamp"].transform("min")
    frame["new_device_flag"] = (frame["transaction_timestamp"] == first_customer_device).astype(int)
    return frame[
        [
            "transaction_id",
            "device_txn_count_24h",
            "device_distinct_customers_24h",
            "device_age_days",
            "device_risk_score",
            "new_device_flag",
        ]
    ]


def _prior_device_customers(frame: pd.DataFrame) -> pd.Series:
    values = pd.Series(0.0, index=frame.index)
    for _, group in frame.groupby("device_id", sort=False):
        ordered = group.sort_values("transaction_timestamp")
        for idx, row in ordered.iterrows():
            start = row["transaction_timestamp"] - pd.Timedelta("24h")
            mask = (ordered["transaction_timestamp"] < row["transaction_timestamp"]) & (
                ordered["transaction_timestamp"] >= start
            )
            values.loc[idx] = ordered.loc[mask, "customer_id"].nunique()
    return values
