# Feature Store Design

V0.2 uses a local DuckDB offline feature store at `data/features/fraud_feature_store.duckdb`. The main table is `transaction_features`, keyed by `transaction_id`.

## Feature Groups

- Customer: transaction velocity, spend totals, failed auths, merchant diversity, country diversity.
- Merchant: transaction volume, fraud rate, average amount, chargeback rate, merchant risk score.
- Device: device volume, distinct customers, device age, device risk score, new-device flag.
- Velocity: short-window activity flags used for fraud operations.
- Transaction: amount z-score, international mismatch, card-not-present, impossible travel, night activity, risky category.

## Point-In-Time Safety

Historical features use rolling windows with `closed="left"` so the current row and future transactions are excluded from aggregate calculations. V0.2 writes `point_in_time_feature_validation.json` and `.csv` to show sampled source timestamps are earlier than the scored transaction.

## Offline Store

DuckDB is used because it is local, fast, SQL-friendly, and easy for reviewers to run without cloud accounts. It approximates an offline feature store pattern without adding Feast or cloud infrastructure too early.

## Enterprise Mapping

In a production deployment:

- Feast or Tecton could define feature views and online/offline stores.
- Snowflake or Databricks could host the offline feature tables.
- Kafka or Redpanda could stream transaction events.
- Airflow could orchestrate batch feature builds.
- MLflow could link model versions to feature store snapshots.

## Feature Freshness and Quality

V0.2 reports row count, feature count, missing rates, zero-variance features, high-null features, feature group quality scores, freshness windows, and overall feature store quality score.

## Feature Lineage Concept

Each feature maps back to raw synthetic transaction, customer, merchant, device, chargeback, or risk-profile inputs. In production this lineage would be captured in a catalog or metadata system.
