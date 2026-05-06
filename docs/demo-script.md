# Three-Minute Demo Script

## 0:00-0:30 - Business Problem

Fraud teams need more than a notebook model. Banks, fintechs, payment processors, and retailers need transaction pipelines, trusted features, explainable risk scores, monitoring, APIs, and alert queues that fraud investigators can actually use.

Position the project in one sentence:

> This project is a production-style fraud feature store and MLOps pipeline built with synthetic payment data.

## 0:30-1:00 - Synthetic Data And Injected Evidence

Run:

```bash
python -m src.data_generation.generate_synthetic_payments
```

Show:

- `data/raw/payment_transactions.csv`
- `data/raw/injected_fraud_pattern_manifest.json`
- `data/raw/injected_data_quality_manifest.json`

Explain that the generator creates fake customers, accounts, merchants, devices, transactions, labels, and controlled fraud/data-quality issues so the pipeline can prove what it catches.

## 1:00-1:45 - Point-In-Time Features And Feature Store

Run:

```bash
python -m src.pipeline.run_all
```

Show:

- `data/features/transaction_features.csv`
- `data/features/fraud_feature_store.duckdb`
- `data/scorecards/point_in_time_feature_validation.json`
- `data/scorecards/feature_store_quality_report.json`

Explain that point-in-time features only use transactions available before the scored transaction timestamp. This avoids leakage, which is one of the most important differences between a real fraud pipeline and a notebook experiment.

## 1:45-2:20 - Model, Registry, Reason Codes, And Alerts

Show:

- `data/scorecards/fraud_model_scorecard.json`
- `models/registry/model_registry.json`
- `docs/model-card.md`
- `data/scoring/scored_transactions.csv`
- `data/scorecards/reason_code_report.json`
- `data/alerts/fraud_alert_queue.csv`

Explain that the model is a deterministic RandomForest baseline. The goal is not to claim production fraud accuracy; the goal is to show repeatable model training, evaluation, registry metadata, score outputs, reason codes, and fraud operations artifacts.

## 2:20-2:45 - Drift Monitoring And Evidence Scorecards

Show:

- `data/scorecards/fraud_pattern_detection_report.json`
- `data/scorecards/data_quality_detection_report.json`
- `data/monitoring/feature_drift_report.csv`
- `data/scorecards/model_monitoring_scorecard.json`
- `data/scorecards/alert_queue_quality_report.json`

Explain that these reports make the project audit-friendly: injected issues are compared with detected issues, score distributions are monitored, and alert quality is summarized.

## 2:45-3:00 - API, Dashboard, And Business Value

Launch API:

```bash
python -m uvicorn src.api.main:app --reload
```

Launch dashboard:

```bash
python -m streamlit run src/dashboard/app.py
```

Mention useful endpoints:

```bash
curl http://127.0.0.1:8000/fraud-summary
curl http://127.0.0.1:8000/model-card
curl http://127.0.0.1:8000/monitoring/drift
```

Close with:

> This project demonstrates the production layer around fraud ML: trusted data, point-in-time features, model evidence, explainable scoring, monitoring, and reviewer-friendly outputs.
