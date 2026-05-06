# LinkedIn Post Drafts

## Version A - Recruiter-Friendly

Status: DRAFT

I built a Payments Fraud Feature Store + MLOps Pipeline as a portfolio project.

This is not a notebook-only fraud model. It shows the production workflow around fraud ML:

- synthetic payment transactions
- injected fraud patterns and data quality issues
- point-in-time feature engineering
- DuckDB offline feature store
- fraud model scorecard
- model registry and model card
- batch/API scoring
- deterministic reason codes
- fraud alert queue
- drift monitoring
- FastAPI and Streamlit
- 61 tests passing
- ruff passing with no pytest warning summary

The goal is to show how payment fraud scoring can be made more reproducible, explainable, and reviewable for data engineering and MLOps teams.

GitHub: [link placeholder]

Screenshot: [screenshot placeholder]

## Version B - Technical Data Engineering / MLOps

Status: DRAFT

I built a local Payments Fraud Feature Store + MLOps Pipeline to demonstrate production-style fraud scoring foundations.

The project goes beyond model training. It includes:

- deterministic synthetic payment data generation
- fraud pattern and data quality manifests
- validation and quarantine outputs
- point-in-time customer, merchant, device, velocity, and transaction features
- DuckDB offline feature store
- RandomForest fraud baseline with model scorecard
- model registry metadata and model card
- batch scoring and FastAPI scoring
- reason codes and recommended actions
- alert queue quality reporting
- PSI, mean shift, missing-rate change, score drift, and monitoring scorecards
- Streamlit dashboard
- Docker, GitHub Actions, pytest, and ruff

Current validation:

- 61 tests passing
- ruff passing
- pipeline passing
- no pytest warning summary

This is meant as a portfolio project for Data Engineering, MLOps, AI Data Engineering, Fraud Data Engineering, and Risk Analytics roles.

GitHub: [link placeholder]

Screenshot: [screenshot placeholder]
