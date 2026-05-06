# Model Card

## Business Objective

Score synthetic payment transactions for fraud risk using trusted point-in-time features, explainable reason codes, and monitoring evidence.

## Model Type

RandomForestClassifier deterministic baseline trained with scikit-learn.

## Training Data

Synthetic customers, accounts, merchants, devices, transactions, chargebacks, and fraud labels generated locally. No real payment or personal data is used.

## Feature Groups

Customer velocity, merchant risk, device risk, transaction context, and point-in-time behavioral aggregates.

## Target Label

`fraud_label`, a deterministic synthetic label produced during fraud pattern injection.

## Threshold Strategy

V0.2 uses a 0.50 prediction threshold and probability-based risk bands: low, medium, high, and critical.

## Reason-Code Approach

Reason codes are deterministic rule explanations mapped from engineered features, not SHAP. They are intended for portfolio demo transparency.

## Metrics

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
  "fraud_capture_rate_top_1_percent": 0.2012,
  "fraud_capture_rate_top_5_percent": 0.3412,
  "fraud_capture_rate_top_10_percent": 0.4004,
  "false_positive_rate": 0.026,
  "model_name": "fraud_risk_random_forest",
  "model_version": "v0.2.0",
  "training_rows": 35817,
  "test_rows": 11939,
  "fraud_rate_train": 0.0425,
  "fraud_rate_test": 0.0425,
  "threshold_used": 0.5,
  "risk_band_distribution": {
    "medium": 10916,
    "low": 753,
    "critical": 169,
    "high": 101
  },
  "top_features_by_importance": [
    {
      "feature_name": "amount_zscore_customer",
      "importance": 0.335161
    },
    {
      "feature_name": "merchant_fraud_rate_30d",
      "importance": 0.119727
    },
    {
      "feature_name": "merchant_risk_score",
      "importance": 0.054266
    },
    {
      "feature_name": "customer_avg_amount_30d",
      "importance": 0.047304
    },
    {
      "feature_name": "merchant_avg_amount_30d",
      "importance": 0.03846
    },
    {
      "feature_name": "device_risk_score",
      "importance": 0.037778
    },
    {
      "feature_name": "customer_txn_count_1h",
      "importance": 0.037597
    },
    {
      "feature_name": "customer_total_amount_24h",
      "importance": 0.037506
    },
    {
      "feature_name": "merchant_chargeback_rate_30d",
      "importance": 0.035514
    },
    {
      "feature_name": "customer_txn_count_24h",
      "importance": 0.035052
    }
  ],
  "model_artifact_path": "/Users/mohmx/portfolio-projects/payments-fraud-feature-store-mlops/models/artifacts/fraud_model.joblib",
  "training_timestamp": "2026-05-06T20:22:50.398424+00:00",
  "evaluation_interpretation": {
    "precision": "Precision estimates how many flagged transactions are truly fraud, which affects investigator workload and customer friction.",
    "recall": "Recall estimates how much known fraud is captured by the model.",
    "pr_auc": "PR AUC is useful for imbalanced fraud data because it focuses on precision-recall tradeoffs.",
    "false_positive_rate": "False positive rate estimates how often legitimate customers could be challenged or delayed."
  }
}
```

## Ethical / Risk Considerations

This model must not be used for real financial decisions. It is synthetic, locally generated, and designed only to demonstrate engineering workflow.

## Monitoring Plan

Monitor feature drift, score distribution shift, alert quality, and model performance when labels are available.

## Future Enhancements

MLflow tracking, Feast feature serving, SHAP explanations, streaming inference, cloud deployment, and human review workflows.
