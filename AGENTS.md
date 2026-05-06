# AGENTS.md

You are building a production-style Data Engineering + MLOps portfolio project.

Project name:
Payments Fraud Feature Store + MLOps Pipeline

Primary goal:
Build a realistic fraud detection data engineering and MLOps system that ingests synthetic payment transactions, creates point-in-time fraud features, trains a model, scores transactions, generates reason codes, monitors drift, and exposes results through API and dashboard layers.

## Business Context

Banks, fintechs, card networks, payment processors, and large retailers need fraud detection systems that are fast, explainable, reliable, and production-ready.

A notebook model is not enough. Enterprise fraud platforms require:
- reliable data ingestion
- data quality checks
- point-in-time feature engineering
- feature store design
- model training
- model registry artifacts
- inference APIs
- batch scoring
- fraud alert queues
- explainable reason codes
- drift monitoring
- operational dashboards
- tests and CI/CD

This project must show how a data engineer / MLOps engineer would build the foundation for a production-style fraud scoring platform.

## Core Outcome

The system should answer:

"Can this transaction be scored for fraud risk using trusted features, monitored model behavior, and explainable reason codes?"

## Build Principles

- Write clean, modular, production-style Python.
- Use Python 3.12.
- Use type hints.
- Use docstrings for public functions.
- Use structured logging.
- Add error handling.
- Use synthetic data only.
- Do not use real financial, payment, customer, merchant, or card data.
- Do not require paid APIs.
- Keep V0.1 deterministic and locally runnable.
- Avoid unnecessary heavy dependencies in V0.1.
- Prefer explainable baseline ML before complex modeling.
- Every feature should be documented.
- Every model output should include metrics and reason codes.
- Every major pipeline stage should have tests.
- Keep README updated after major changes.

## Required Architecture

The repo should contain these layers:

1. Synthetic data generation
2. Fraud pattern injection
3. Transaction ingestion
4. Data quality validation
5. Feature engineering
6. Offline feature store
7. Training dataset creation
8. Model training
9. Model registry artifacts
10. Batch scoring
11. API scoring
12. Reason-code generation
13. Drift monitoring
14. Fraud alert queue
15. FastAPI service
16. Streamlit dashboard
17. Tests
18. Documentation
19. CI/CD
20. Docker

## Expected Folder Structure

```text
payments-fraud-feature-store-mlops/
  README.md
  AGENTS.md
  architecture/
    architecture.md
    data-flow.md
    star-story.md
  config/
    settings.yaml
    data_quality_rules.yaml
    feature_definitions.yaml
    model_config.yaml
    monitoring_rules.yaml
  data/
    raw/
    processed/
    features/
    training/
    scoring/
    alerts/
    monitoring/
    scorecards/
  docs/
    business-problem.md
    data-dictionary.md
    implementation-plan.md
    metrics.md
    feature-store-design.md
    model-card.md
    monitoring-design.md
    demo-script.md
    linkedin-post.md
    recruiter-summary.md
    technical-deep-dive.md
    sample-outputs.md
  models/
    registry/
    artifacts/
  notebooks/
    01_data_exploration.ipynb
  src/
    __init__.py
    common/
      __init__.py
      config.py
      logging.py
      paths.py
    data_generation/
      __init__.py
      generate_synthetic_payments.py
    ingestion/
      __init__.py
      loaders.py
      validators.py
    quality/
      __init__.py
      rules.py
      checks.py
      quarantine.py
    features/
      __init__.py
      customer_features.py
      merchant_features.py
      device_features.py
      velocity_features.py
      feature_store.py
      build_features.py
    training/
      __init__.py
      dataset.py
      train_model.py
      evaluate_model.py
      registry.py
    scoring/
      __init__.py
      score_batch.py
      score_transaction.py
      reason_codes.py
      alert_queue.py
    monitoring/
      __init__.py
      drift.py
      performance.py
      monitor.py
    api/
      __init__.py
      main.py
      schemas.py
    dashboard/
      __init__.py
      app.py
    pipeline/
      __init__.py
      run_all.py
  tests/
    unit/
    integration/
    monitoring/
  .github/
    workflows/
      ci.yml
  .env.example
  .gitignore
  .python-version
  Dockerfile
  docker-compose.yml
  Makefile
  pyproject.toml
  requirements.txt
```

## Synthetic Data Requirements

Generate synthetic datasets for:

customers
accounts
merchants
devices
payment_transactions
chargebacks
fraud_labels
merchant_risk_profiles
device_risk_profiles

Each dataset should include realistic but fake fields.

## Transaction Data Fields

Transactions should include:

transaction_id
customer_id
account_id
merchant_id
device_id
transaction_timestamp
amount
currency
payment_channel
merchant_category
merchant_country
customer_country
card_present_flag
is_international
auth_result
ip_country
device_fingerprint
transaction_status
fraud_label

## Fraud Pattern Injection

Inject controlled fraud patterns such as:

high-velocity transactions
impossible travel
new device high-value purchase
merchant risk spike
international transaction mismatch
repeated declined attempts followed by approval
account takeover pattern
unusual merchant category
amount outlier
night-time transaction burst
card-not-present fraud pattern
synthetic chargeback pattern

Record injected patterns in:

data/raw/injected_fraud_pattern_manifest.json

## Data Quality Issues

Inject controlled data quality issues such as:

duplicate transactions
missing customer_id
invalid merchant_id
invalid device_id
negative transaction amount
future transaction timestamp
invalid currency
missing fraud_label
inconsistent country codes
transactions linked to closed accounts

Record data quality issues in:

data/raw/injected_data_quality_manifest.json

## Feature Store Requirements

Create an offline feature store using DuckDB.

Feature groups:

Customer Features
customer_txn_count_1h
customer_txn_count_24h
customer_total_amount_24h
customer_avg_amount_30d
customer_failed_auth_count_24h
customer_distinct_merchants_24h
customer_distinct_countries_24h
Merchant Features
merchant_txn_count_24h
merchant_fraud_rate_30d
merchant_avg_amount_30d
merchant_chargeback_rate_30d
merchant_risk_score
Device Features
device_txn_count_24h
device_distinct_customers_24h
device_age_days
device_risk_score
new_device_flag
Transaction Features
amount_zscore_customer
international_mismatch_flag
card_not_present_flag
impossible_travel_flag
night_transaction_flag
high_velocity_flag
risky_merchant_category_flag

Point-in-time correctness matters. Features must not use future transactions when calculating historical features.

## Model Requirements

Train a deterministic baseline model using scikit-learn.

Use one of:

LogisticRegression
RandomForestClassifier
HistGradientBoostingClassifier

The model output should include:

fraud_probability
fraud_prediction
risk_band
reason_codes

Metrics:

precision
recall
f1_score
roc_auc
pr_auc
confusion_matrix
fraud_capture_rate_top_5_percent
false_positive_rate

Save model artifacts to:

models/artifacts/
models/registry/model_registry.json

## Reason Code Requirements

Generate reason codes without requiring SHAP in V0.1.

Examples:

HIGH_VELOCITY_CUSTOMER
NEW_DEVICE_HIGH_VALUE
INTERNATIONAL_MISMATCH
RISKY_MERCHANT
AMOUNT_OUTLIER
MULTIPLE_FAILED_AUTHS
NIGHT_TRANSACTION_BURST
DEVICE_LINKED_TO_MULTIPLE_CUSTOMERS

Each scored transaction should include:

top_reason_codes
reason_code_descriptions
risk_band
recommended_action

Recommended actions:

approve
step_up_authentication
manual_review
decline

## Monitoring Requirements

Create deterministic monitoring reports.

Reports:

data/monitoring/feature_drift_report.csv
data/monitoring/feature_drift_summary.json
data/monitoring/scoring_distribution_report.csv
data/monitoring/model_performance_report.json

Drift metrics:

population_stability_index
mean_shift
missing_rate_change
category_distribution_shift

## API Requirements

Create FastAPI endpoints:

GET /health
GET /features
GET /model-card
GET /monitoring/drift
GET /alerts
POST /score-transaction
POST /score-batch
GET /scorecards
GET /fraud-summary

## Dashboard Requirements

Create a Streamlit dashboard with sections:

Executive Overview
Fraud Model Performance
Feature Store Overview
Fraud Alerts
Transaction Scoring Lab
Reason Code Explorer
Drift Monitoring
Data Quality Issues
Model Card
Investigator Queue

## Evaluation / Scorecard Requirements

Generate:

data/scorecards/fraud_model_scorecard.json
data/scorecards/fraud_model_scorecard.csv
data/scorecards/feature_store_quality_report.json
data/scorecards/feature_store_quality_report.csv
data/scorecards/scoring_quality_report.json
data/scorecards/scoring_quality_report.csv

## Required Commands

Use these commands where possible:

pip install -r requirements.txt
python -m src.data_generation.generate_synthetic_payments
python -m src.pipeline.run_all
python -m pytest
python -m ruff check .
streamlit run src/dashboard/app.py
uvicorn src.api.main:app --reload

## Makefile Commands

Create a Makefile with:

make install
make generate-data
make run-pipeline
make train-model
make score-batch
make monitor
make test
make lint
make format
make dashboard
make api
make docker-up
make docker-down

## Testing Requirements

Add tests for:

synthetic data generation
fraud pattern manifest creation
data quality manifest creation
ingestion
data quality validation
quarantine output
point-in-time feature correctness
customer velocity features
merchant risk features
device features
feature store creation
training dataset creation
model training
model registry creation
batch scoring
single transaction scoring
reason code generation
risk band assignment
alert queue creation
PSI calculation
drift report creation
API health endpoint
API score transaction endpoint
API fraud summary endpoint
full pipeline execution

Target at least 25 tests by V0.1.

## Definition of Done

A task is complete only when:

Code runs locally.
Tests pass.
Ruff passes.
README is updated.
Metrics are documented.
Feature definitions are documented.
Model card exists.
Monitoring reports exist.
Dashboard can run.
API endpoints return valid JSON.
GitHub Actions workflow exists.
Docker files exist.
STAR story is documented.
LinkedIn post draft is included.
No real sensitive data is used.
