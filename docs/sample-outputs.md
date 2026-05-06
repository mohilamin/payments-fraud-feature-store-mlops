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
  "scored_transactions": 49800,
  "alert_count": 1200,
  "average_fraud_probability": 0.08
}
```
