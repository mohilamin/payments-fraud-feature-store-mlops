# Technical Deep Dive

V0.1 uses deterministic synthetic data and a RandomForest baseline so reviewers can run the system locally. DuckDB provides a lightweight offline feature store. The feature calculations use prior rolling windows so labels and future transactions do not leak into historical features.

In production, Kafka or Redpanda could stream events, Feast or Tecton could manage feature serving, MLflow could track model lifecycle, and Snowflake or Databricks could host warehouse-scale training data.
