# Technical Deep Dive

## Architecture Decisions

V0.3 keeps the system local, deterministic, and easy to validate from a fresh clone. The repo is separated into generation, ingestion, quality checks, feature engineering, feature store persistence, training, scoring, monitoring, API, dashboard, and evidence reporting layers.

The design goal is credibility without unnecessary infrastructure. A reviewer can run the full system locally, inspect the artifacts, and understand how the same pattern would map to an enterprise stack.

## Why DuckDB Was Used Locally

DuckDB provides a small, fast SQL engine for the offline feature store. It avoids requiring Snowflake, Databricks, or cloud credentials while still demonstrating:

- durable feature tables
- SQL-readable outputs
- local analytics performance
- a clear boundary between feature engineering and model training
- reproducible feature artifacts for tests and demos

In a larger deployment, the same feature tables could move to Snowflake, Databricks, BigQuery, Redshift, or a lakehouse table format.

## Why RandomForest Was Used

The model is a deterministic RandomForest baseline from scikit-learn. It was chosen because it works well enough for tabular synthetic fraud features, supports reproducible training with `random_state`, exposes feature importances, and avoids heavy dependencies.

The project is not claiming production fraud performance. The purpose is to show the full MLOps workflow around fraud scoring.

## How Point-In-Time Features Work

Customer, merchant, and device features are calculated using rolling historical windows. The feature logic uses events before the current transaction timestamp, so a transaction cannot benefit from future behavior.

Examples:

- `customer_txn_count_1h` counts prior customer transactions in the last hour.
- `customer_total_amount_24h` sums prior customer spend in the last 24 hours.
- `merchant_fraud_rate_30d` uses prior fraud labels available before the current transaction.
- `device_txn_count_24h` counts prior activity for the device.

The pipeline writes `point_in_time_feature_validation.json` and `.csv` to show sampled transactions, source timestamps, and pass/fail status.

## How Feature Store Quality Is Measured

The feature store quality report checks:

- total feature rows
- total features
- missing rate by feature
- zero-variance features
- high-null features
- feature freshness
- point-in-time validation pass rate
- feature group quality scores
- overall feature store quality score

This gives reviewers evidence that feature tables are not just generated, but assessed.

## How Fraud Pattern Detection Evidence Works

The generator writes `injected_fraud_pattern_manifest.json` with known pattern types and transaction IDs. After scoring, the evidence layer compares those expected IDs to scored transactions and risk bands.

The report tracks:

- total injected patterns
- detected and missed patterns
- detection rate
- detection rate by pattern type
- expected transaction IDs
- detected transaction IDs
- matched and missed counts
- average fraud probability by pattern

This makes the demo measurable instead of anecdotal.

## How Data Quality Detection Evidence Works

The generator also writes `injected_data_quality_manifest.json`. Validation outputs are compared with the manifest to produce detection rates for duplicate transactions, missing IDs, invalid merchants/devices, negative amounts, future timestamps, invalid currencies, missing labels, country-code issues, and closed-account transactions.

## How Reason Codes Are Generated

Reason codes are deterministic rules mapped from engineered features and transaction context. They are intentionally explainable and dependency-light.

Examples:

- high customer velocity
- new device high-value purchase
- international mismatch
- risky merchant
- amount outlier
- multiple failed auths
- night transaction burst
- card-not-present risk
- impossible travel

In production, these operational reason codes could be supplemented with SHAP or another model explanation method.

## How The Alert Queue Is Prioritized

Scored transactions receive a fraud probability and risk band. High and critical risk transactions are written to the fraud alert queue with reason codes and recommended actions:

- approve
- step_up_authentication
- manual_review
- decline

The alert queue quality report summarizes alert volume, risk-band mix, recommended action mix, confirmed fraud rate in alerts, and top reason codes.

## How Drift Monitoring Works

The monitoring layer compares baseline and current slices of the generated feature/scoring population. It writes:

- PSI by feature
- mean shift by feature
- missing-rate change
- fraud score distribution shift
- risk-band distribution shift
- drift severity
- monitoring summary score

This is batch monitoring, not a live observability platform, but it demonstrates the mechanics of model monitoring evidence.

## How This Could Scale

- Kafka or Redpanda: stream payment authorization events into the feature pipeline.
- Feast: manage offline and online feature definitions.
- MLflow: track experiments, register models, and manage promotion workflows.
- Spark: compute large-scale rolling features.
- Snowflake: store warehouse-scale transaction and feature tables.
- Databricks: combine Spark feature jobs, Delta tables, and model workflows.
- Airflow: orchestrate generation, validation, feature builds, training, scoring, and monitoring.
- Cloud deployment: host API, dashboard, object storage, feature store, and scheduled jobs.

## Known Limitations

- Synthetic data only.
- Local DuckDB feature store.
- Baseline scikit-learn model.
- Deterministic reason codes, not SHAP.
- Batch monitoring only.
- No live Kafka stream.
- No cloud deployment.
- No authentication or role-based access.
- No MLflow or Feast yet.

## Future Enhancements

- Kafka/Redpanda streaming ingestion.
- Feast feature store.
- MLflow experiment tracking and model registry.
- SHAP reason codes.
- Spark/Databricks feature computation.
- Snowflake warehouse version.
- Airflow orchestration.
- Cloud deployment.
- Auth and role-based access.
- Real-time drift alerts.
