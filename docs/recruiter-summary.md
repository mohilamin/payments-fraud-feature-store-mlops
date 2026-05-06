# Recruiter Summary

## Simple Explanation

This project shows how a payment fraud detection system works beyond a machine learning notebook.

Fraud teams do not only need a model. They need reliable transaction data, trustworthy features, model evidence, risk scores, explanations, monitoring, and a queue of alerts that investigators can review.

## What Problem It Solves

Banks, fintechs, payment processors, and retailers need to detect risky transactions while limiting customer friction. A model that works in a notebook is not enough unless the surrounding data and MLOps workflow is reliable.

## What Was Built

This repo builds a local end-to-end system using synthetic payment data:

- Generates fake customers, accounts, merchants, devices, transactions, fraud labels, and chargebacks.
- Injects known fraud patterns and data quality issues.
- Validates data and writes detection evidence.
- Builds point-in-time fraud features so the model does not use future information.
- Stores features in DuckDB as a local offline feature store.
- Trains a deterministic fraud model.
- Writes model metrics, a model registry artifact, and a model card.
- Scores transactions with risk bands, reason codes, and recommended actions.
- Creates a fraud alert queue.
- Produces drift monitoring and scorecard reports.
- Exposes outputs through FastAPI and Streamlit.
- Runs with 61 passing tests and ruff validation.

## Skills It Proves

- Data engineering pipeline design
- Feature engineering and feature store design
- MLOps artifacts such as model cards, model registries, scorecards, and monitoring reports
- Fraud/risk analytics workflow understanding
- API and dashboard delivery
- Testing, linting, Docker, and CI/CD readiness
- Business communication for technical projects

## Why It Matters For Roles

- Data Engineer: shows ingestion, validation, feature pipelines, DuckDB storage, and reproducibility.
- MLOps Engineer: shows training, registry artifacts, scoring, monitoring, Docker, tests, and CI.
- Fraud Data Engineer: shows fraud pattern injection, risk scoring, reason codes, and alert queues.
- AI Data Engineer: shows governed feature generation and model-ready data products.
- Risk Analytics Engineer: shows model scorecards, false positive thinking, and investigator-friendly outputs.

## Why It Is Stronger Than A Basic ML Notebook

It includes the production evidence around the model: point-in-time validation, data quality detection reports, fraud pattern detection reports, model registry metadata, reason-code coverage, alert queue quality, drift monitoring, API schemas, dashboard views, and 61 passing tests.
