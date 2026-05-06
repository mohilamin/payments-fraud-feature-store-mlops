# Model Card

Model: RandomForestClassifier baseline for synthetic payment fraud.

Purpose: score synthetic payment transactions for fraud risk using point-in-time features.

Limitations: synthetic data only, deterministic baseline, no SHAP or production monitoring service.

Metrics:

```json
{
  "precision": 0.3627,
  "recall": 0.3333,
  "f1_score": 0.3474,
  "roc_auc": 0.7086,
  "pr_auc": 0.3429,
  "confusion_matrix": [
    [
      11135,
      297
    ],
    [
      338,
      169
    ]
  ],
  "fraud_capture_rate_top_5_percent": 0.3412,
  "false_positive_rate": 0.026
}
```
