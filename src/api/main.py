from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI

from src.api.schemas import ScoreTransactionRequest
from src.common.config import get_path
from src.scoring.score_batch import score_batch
from src.scoring.score_transaction import score_transaction

app = FastAPI(title="Payments Fraud Feature Store + MLOps Pipeline")


def _csv(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return pd.read_csv(path).fillna("").head(200).to_dict("records")


def _json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "payments-fraud-feature-store-mlops"}


@app.get("/features")
def features() -> list[dict[str, object]]:
    return _csv(get_path("features") / "transaction_features.csv")


@app.get("/model-card")
def model_card() -> dict[str, str]:
    path = Path("docs/model-card.md")
    return {"content": path.read_text(encoding="utf-8") if path.exists() else ""}


@app.get("/monitoring/drift")
def drift() -> dict[str, object]:
    return _json(get_path("monitoring") / "feature_drift_summary.json")


@app.get("/alerts")
def alerts() -> list[dict[str, object]]:
    return _csv(get_path("alerts") / "fraud_alert_queue.csv")


@app.post("/score-transaction")
def score_transaction_endpoint(request: ScoreTransactionRequest) -> dict[str, object]:
    return score_transaction(request.model_dump())


@app.post("/score-batch")
def score_batch_endpoint() -> dict[str, object]:
    scored = score_batch()
    return {"scored_transactions": int(len(scored)), "alerts": int(scored["risk_band"].isin(["high", "critical"]).sum())}


@app.get("/scorecards")
def scorecards() -> dict[str, object]:
    return {
        "model": _json(get_path("scorecards") / "fraud_model_scorecard.json"),
        "feature_store": _json(get_path("scorecards") / "feature_store_quality_report.json"),
        "scoring": _json(get_path("scorecards") / "scoring_quality_report.json"),
    }


@app.get("/fraud-summary")
def fraud_summary() -> dict[str, object]:
    scored_path = get_path("scoring") / "scored_transactions.csv"
    alerts_path = get_path("alerts") / "fraud_alert_queue.csv"
    if not scored_path.exists():
        return {}
    scored = pd.read_csv(scored_path)
    alerts_df = pd.read_csv(alerts_path) if alerts_path.exists() else pd.DataFrame()
    return {
        "scored_transactions": int(len(scored)),
        "alert_count": int(len(alerts_df)),
        "average_fraud_probability": round(float(scored["fraud_probability"].mean()), 4),
        "high_or_critical_rate": round(float(scored["risk_band"].isin(["high", "critical"]).mean()), 4),
    }
