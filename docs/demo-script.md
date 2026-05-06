# Demo Script

## 0:00-0:30 - Business Problem

Explain that fraud systems need more than a notebook model. They need reliable features, reason codes, monitoring, APIs, and operational alerts.

## 0:30-1:00 - Generate Data

```bash
python -m src.data_generation.generate_synthetic_payments
```

Show raw synthetic datasets and injected manifests.

## 1:00-1:45 - Run Pipeline

```bash
python -m src.pipeline.run_all
```

Show quality issues, feature store outputs, and DuckDB artifact.

## 1:45-2:30 - Model and Scoring

Show model scorecard, model registry, scored transactions, reason codes, and alert queue.

## 2:30-3:00 - Monitoring and Apps

Show drift reports, FastAPI endpoints, and the Streamlit dashboard.
