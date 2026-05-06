# Technical Deep Dive

## Architecture Decisions

V0.2 keeps the architecture local and deterministic so reviewers can run it quickly. The project separates generation, ingestion, quality, features, training, scoring, monitoring, API, dashboard, and evidence reports.

## Why DuckDB

DuckDB provides a local SQL analytics engine that behaves like a small offline feature store. It avoids cloud setup while still demonstrating feature-table persistence, SQL access, and reproducible local artifacts.

## Why RandomForest

RandomForestClassifier is a practical baseline for tabular fraud features. It is deterministic with `random_state`, exposes feature importances, and avoids heavier gradient boosting or deep learning dependencies in V0.2.

## Point-In-Time Features

Customer, merchant, and device features use rolling windows with prior events only. V0.2 adds explicit validation reports proving sampled feature calculations do not use future transactions.

## Fraud Pattern Detection Evidence

The synthetic generator records injected fraud pattern transaction IDs. The evidence layer compares those IDs against scored transactions and risk bands, producing matched counts, missed counts, and detection rates by pattern type.

## Data Quality Detection Evidence

Injected data quality manifests are compared against validation output. The report tracks expected IDs, detected IDs, matched records, missed records, false positives where feasible, and detection rates by issue type.

## Reason Codes

Reason codes are deterministic rules mapped from engineered features and fraud probability. They are intentionally simple and explainable. In production, SHAP or another model explanation approach could supplement these operational reason codes.

## Alert Queue Prioritization

High and critical risk transactions become alerts. Critical alerts have highest investigator priority. Each alert includes risk band, recommended action, reason codes, and fraud probability.

## Scale-Out Path

- Kafka or Redpanda for streaming transactions.
- Feast or Tecton for feature store definitions and online serving.
- MLflow for model experiments, registry, and promotion.
- Spark for distributed feature computation.
- Snowflake or Databricks for warehouse-scale offline features.
- Airflow for orchestration.
- Cloud deployment with authenticated APIs and role-based dashboards.
