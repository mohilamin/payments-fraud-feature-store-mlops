# GitHub Profile Setup

## Suggested Repo Description

Production-style fraud feature store and MLOps pipeline for synthetic payment transactions, point-in-time features, model scoring, reason codes, alert queues, and drift monitoring.

## Suggested Topics

- fraud-detection
- mlops
- feature-store
- data-engineering
- payments
- risk-analytics
- machine-learning
- fastapi
- streamlit
- duckdb
- python
- model-monitoring
- portfolio-project

## Pinned Repo Blurb

Production-style fraud MLOps project that turns synthetic payment events into point-in-time features, trains a baseline fraud model, scores transactions with reason codes, monitors drift, and exposes results through FastAPI and Streamlit.

## Suggested README Headline

Fraud Feature Store + MLOps Pipeline For Synthetic Payment Risk Scoring

## GitHub Profile Project Summary

This project demonstrates the production workflow around fraud machine learning: trusted data generation, quality checks, point-in-time feature engineering, an offline DuckDB feature store, model scorecards, registry metadata, reason codes, alert queues, drift monitoring, tests, API serving, and dashboard review.

## How To Describe This In Interviews

Use this framing:

> I built a local fraud feature store and MLOps pipeline to show the engineering system around a fraud model. The project generates synthetic payment data, injects known fraud and data quality issues, validates them, creates point-in-time features, stores them in DuckDB, trains a baseline model, scores transactions, generates reason codes, creates alerts, monitors drift, and exposes the outputs through API and dashboard layers.

Then emphasize the evidence:

- 61 passing tests
- point-in-time validation report
- fraud pattern detection report
- data quality detection report
- model scorecard and model registry
- reason-code coverage report
- alert queue quality report
- drift monitoring scorecard
