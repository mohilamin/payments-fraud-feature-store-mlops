from __future__ import annotations

import pandas as pd

from src.features.customer_features import build_customer_features
from src.features.device_features import build_device_features
from src.features.feature_store import write_feature_store
from src.features.merchant_features import build_merchant_features

RISKY_CATEGORIES = {"crypto", "gaming", "jewelry"}


def build_transaction_features(frames: dict[str, pd.DataFrame], clean_transactions: pd.DataFrame) -> pd.DataFrame:
    """Build the V0.1 feature table."""
    txns = clean_transactions.copy()
    txns["transaction_timestamp"] = pd.to_datetime(txns["transaction_timestamp"], errors="coerce")
    txns["amount"] = pd.to_numeric(txns["amount"], errors="coerce").fillna(0)
    txns["fraud_label"] = pd.to_numeric(txns["fraud_label"], errors="coerce").fillna(0).astype(int)
    txns = txns.sort_values("transaction_timestamp").reset_index(drop=True)
    customer = build_customer_features(txns)
    merchant = build_merchant_features(txns, frames["merchant_risk_profiles"], frames["chargebacks"])
    device = build_device_features(txns, frames["devices"], frames["device_risk_profiles"])
    features = txns[
        [
            "transaction_id",
            "customer_id",
            "account_id",
            "merchant_id",
            "device_id",
            "transaction_timestamp",
            "amount",
            "fraud_label",
            "payment_channel",
            "merchant_category",
            "merchant_country",
            "customer_country",
            "ip_country",
            "auth_result",
        ]
    ].merge(customer, on="transaction_id").merge(merchant, on="transaction_id").merge(device, on="transaction_id")
    std = features.groupby("customer_id")["amount"].transform("std").replace(0, pd.NA)
    mean = features.groupby("customer_id")["amount"].transform("mean")
    features["amount_zscore_customer"] = ((features["amount"] - mean) / std).fillna(0).clip(-10, 10)
    features["international_mismatch_flag"] = (
        (features["merchant_country"] != features["customer_country"]) | (features["ip_country"] != features["customer_country"])
    ).astype(int)
    features["card_not_present_flag"] = (features["payment_channel"] == "card_not_present").astype(int)
    features["impossible_travel_flag"] = (
        features["international_mismatch_flag"].eq(1) & features["customer_txn_count_1h"].gt(0)
    ).astype(int)
    features["night_transaction_flag"] = features["transaction_timestamp"].dt.hour.between(0, 4).astype(int)
    features["high_velocity_flag"] = features["customer_txn_count_1h"].ge(5).astype(int)
    features["risky_merchant_category_flag"] = features["merchant_category"].isin(RISKY_CATEGORIES).astype(int)
    write_feature_store(features)
    return features
