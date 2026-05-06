# Sample Outputs

## Scored Transaction

```json
{
  "transaction_id": "T0000123",
  "fraud_probability": 0.82,
  "risk_band": "high",
  "top_reason_codes": ["HIGH_VELOCITY_CUSTOMER", "INTERNATIONAL_MISMATCH"],
  "recommended_action": "manual_review"
}
```

## Fraud Summary

```json
{
  "total_scored_transactions": 49800,
  "total_alerts": 1200,
  "average_fraud_probability": 0.08,
  "model_version": "v0.2.0"
}
```

## Fraud Pattern Detection

```json
{
  "pattern_type": "high_velocity_transactions",
  "matched_transaction_count": 120,
  "missed_transaction_count": 60,
  "pass_fail": "pass"
}
```

## Point-in-Time Validation

```json
{
  "feature_name": "customer_txn_count_24h",
  "sampled_transaction_id": "T0001234",
  "point_in_time_safe": true
}
```

## Reason Code Report

```json
{
  "reason_code_coverage_rate": 100.0,
  "top_reason_codes": ["RISKY_MERCHANT", "CARD_NOT_PRESENT_RISK"]
}
```
