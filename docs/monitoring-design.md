# Monitoring Design

V0.2 monitoring is deterministic and local. It is designed to show how a fraud MLOps pipeline can produce audit-friendly evidence without external services.

## Feature Drift

The pipeline compares the first half of generated features to the second half and calculates PSI, mean shift, and missing-rate change. Drift severity is classified as low, medium, or high.

## Score Drift

Fraud score distribution shift is calculated by comparing average fraud probability across the baseline and current scoring slices. Risk-band distribution is also tracked.

## Label and Performance Monitoring

Because this synthetic dataset includes labels, the pipeline writes a local model performance report from scored transactions. In production, labels would arrive later from chargebacks, investigations, confirmed fraud, and customer disputes.

## Alert Queue Monitoring

The alert queue quality report tracks alert count, risk-band mix, recommended action mix, confirmed fraud rate in alerts, manual review volume, decline volume, and alert precision estimate.

## Production Version

A real deployment would schedule monitoring runs, store history, trigger alerts, integrate with Slack/PagerDuty/Jira, compare against SLA thresholds, and link reports to model registry versions.

## Future Enhancements

- Live scoring drift dashboards.
- MLflow model monitoring artifacts.
- Kafka-based streaming score distribution checks.
- Feature freshness SLAs.
- Human investigation outcome feedback loop.
