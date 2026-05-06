from __future__ import annotations

from pydantic import BaseModel, Field


class ScoreTransactionRequest(BaseModel):
    transaction_id: str = "ad_hoc"
    amount: float = 250.0
    customer_txn_count_1h: float = 0.0
    customer_txn_count_24h: float = 1.0
    customer_total_amount_24h: float = 250.0
    customer_avg_amount_30d: float = 100.0
    customer_failed_auth_count_24h: float = 0.0
    customer_distinct_merchants_24h: float = 1.0
    customer_distinct_countries_24h: float = 1.0
    merchant_txn_count_24h: float = 10.0
    merchant_fraud_rate_30d: float = 0.01
    merchant_avg_amount_30d: float = 100.0
    merchant_chargeback_rate_30d: float = 0.01
    merchant_risk_score: float = 0.05
    device_txn_count_24h: float = 1.0
    device_distinct_customers_24h: float = 1.0
    device_age_days: float = 100.0
    device_risk_score: float = 0.05
    new_device_flag: int = 0
    amount_zscore_customer: float = 0.0
    international_mismatch_flag: int = 0
    card_not_present_flag: int = 1
    impossible_travel_flag: int = 0
    night_transaction_flag: int = 0
    high_velocity_flag: int = 0
    risky_merchant_category_flag: int = 0
    fraud_label: int = Field(default=0, exclude=True)
