# Architecture

This project is a local production-style fraud scoring platform.

Layers:

1. Synthetic payment data generation creates fake customers, accounts, merchants, devices, transactions, labels, risk profiles, and chargebacks.
2. Quality validation detects duplicate, missing, invalid, future-dated, and closed-account transactions.
3. Feature engineering creates point-in-time customer, merchant, device, and transaction features.
4. DuckDB stores the offline transaction feature table.
5. scikit-learn trains a deterministic fraud model and writes registry artifacts.
6. Scoring generates probabilities, risk bands, reason codes, recommended actions, and alert queues.
7. Monitoring writes drift, score distribution, and performance reports.
8. FastAPI and Streamlit expose the outputs for demo and review.
