# Feature Store Design

The V0.1 offline feature store is a local DuckDB database at `data/features/fraud_feature_store.duckdb`.

The main table is `transaction_features`. It is keyed by `transaction_id` and includes transaction time, entity identifiers, labels, and engineered features.

Point-in-time safety is handled by using rolling windows with `closed="left"` so each row only uses transactions before the event timestamp.

In a production version, this layer could map to Feast, Tecton, Snowflake, Databricks, or a streaming feature system.
