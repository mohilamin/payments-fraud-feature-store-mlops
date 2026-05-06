# Payments Fraud Feature Store + MLOps Pipeline

## Business Problem

Banks, fintechs, payment processors, and large retailers need fraud detection systems that are fast, explainable, reliable, and production-ready.

A notebook fraud model is not enough for enterprise use. Companies need transaction ingestion, data quality checks, point-in-time feature engineering, feature storage, model training, model versioning, inference APIs, fraud reason codes, drift monitoring, and dashboards for fraud operations.

## Project Goal

Build a production-style Data Engineering + MLOps portfolio project that demonstrates how payment transaction data can be transformed into fraud features, used to train a fraud model, scored through an API, monitored for drift, and reviewed through an investigator dashboard.

## Core Business Question

Can this transaction be scored for fraud risk using trusted features, explainable reason codes, and monitored model behavior?

## Key Features

- Synthetic payment transaction generation
- Customer, merchant, device, and account data generation
- Fraud pattern injection
- Data quality validation
- Point-in-time feature engineering
- Offline feature store using DuckDB
- Fraud model training with scikit-learn
- Model metrics and model registry artifacts
- Batch fraud scoring
- API-based fraud scoring
- Reason-code generation
- Drift monitoring
- Fraud alert queue
- FastAPI service layer
- Streamlit fraud operations dashboard
- Docker support
- GitHub Actions CI
- pytest test coverage

## Target Users

- Data Engineering teams
- MLOps teams
- Fraud analytics teams
- Risk operations teams
- Fintech platform teams
- Payment processing teams
- Model governance teams

## Tech Stack

- Python 3.12
- Pandas
- NumPy
- scikit-learn
- DuckDB
- FastAPI
- Streamlit
- pytest
- ruff
- Docker
- GitHub Actions

Optional future enhancements:
- MLflow
- Feast
- Kafka / Redpanda
- Spark
- Snowflake / Databricks
- SHAP
- Airflow
- Cloud deployment

## STAR Story

### Situation
Payment organizations need fraud detection systems that are accurate, explainable, and production-ready, but many prototypes stop at model training and do not include feature reliability, monitoring, or operational review.

### Task
Build an end-to-end fraud feature store and MLOps pipeline that ingests transactions, engineers point-in-time features, trains a model, scores fraud risk, generates reason codes, monitors drift, and supports investigator review.

### Action
Designed synthetic payment data generation, fraud pattern injection, validation rules, feature pipelines, DuckDB feature store, model training, scoring, model registry artifacts, drift monitoring, API endpoints, dashboard views, tests, and CI/CD.

### Result
Created a reproducible portfolio project that demonstrates enterprise-style fraud detection foundations with feature engineering, model scoring, explainability, monitoring, and operational evidence.

## Project Status

Phase 1: Repository bootstrap and first working version.
