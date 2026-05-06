# Fresh Clone Validation

Use this when validating the project from a clean local checkout.

## Clone

```bash
cd /Users/mohmx/portfolio-projects
git clone https://github.com/mohilamin/payments-fraud-feature-store-mlops.git
cd payments-fraud-feature-store-mlops
```

If the repo already exists locally:

```bash
cd /Users/mohmx/portfolio-projects/payments-fraud-feature-store-mlops
git pull
```

## Create Conda Environment

```bash
conda create -n fraud-mlops python=3.12 -y
conda activate fraud-mlops
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Generate Data

```bash
python -m src.data_generation.generate_synthetic_payments
```

## Run Pipeline

```bash
python -m src.pipeline.run_all
```

Expected outputs include:

- `data/features/fraud_feature_store.duckdb`
- `models/artifacts/fraud_model.joblib`
- `models/registry/model_registry.json`
- `data/scoring/scored_transactions.csv`
- `data/alerts/fraud_alert_queue.csv`
- `data/scorecards/fraud_model_scorecard.json`
- `data/scorecards/model_monitoring_scorecard.json`

## Run Tests

```bash
python -m pytest
```

Expected result:

```text
61 passed
```

## Run Ruff

```bash
python -m ruff check .
```

Expected result:

```text
All checks passed!
```

## Launch Dashboard

```bash
python -m streamlit run src/dashboard/app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

## Launch API

```bash
python -m uvicorn src.api.main:app --reload
```

Useful endpoints:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/fraud-summary
curl http://127.0.0.1:8000/model-card
curl http://127.0.0.1:8000/monitoring/drift
```
