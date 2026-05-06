# Monitoring Design

V0.1 monitoring writes deterministic local reports:

- `feature_drift_report.csv`
- `feature_drift_summary.json`
- `scoring_distribution_report.csv`
- `model_performance_report.json`

Feature drift compares the first half of generated features to the second half using PSI, mean shift, and missing-rate change.
