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
def features() -> dict[str, object]:
    definitions_path = Path("config/feature_definitions.yaml")
    feature_quality = _json(get_path("scorecards") / "feature_store_quality_report.json")
    rows = _csv(get_path("features") / "transaction_features.csv")
    return {
        "feature_groups": feature_quality.get("feature_group_quality_score", {}),
        "feature_descriptions": definitions_path.read_text(encoding="utf-8") if definitions_path.exists() else "",
        "row_count": feature_quality.get("total_feature_rows", len(rows)),
        "quality_score": feature_quality.get("overall_feature_store_quality_score"),
        "sample_rows": rows[:10],
    }


@app.get("/model-card")
def model_card() -> dict[str, object]:
    path = Path("docs/model-card.md")
    registry = _json(get_path("model_registry") / "model_registry.json")
    return {
        "model_name": registry.get("model_name"),
        "model_version": registry.get("model_version"),
        "metrics": registry.get("metrics", {}),
        "intended_use": registry.get("intended_use"),
        "limitations": registry.get("known_limitations", []),
        "threshold_strategy": registry.get("thresholds", {}),
        "content": path.read_text(encoding="utf-8") if path.exists() else "",
    }


@app.get("/monitoring/drift")
def drift() -> dict[str, object]:
    summary = _json(get_path("monitoring") / "feature_drift_summary.json")
    scorecard = _json(get_path("scorecards") / "model_monitoring_scorecard.json")
    return {
        "overall_drift_status": summary.get("overall_drift_status", scorecard.get("overall_drift_status")),
        "high_drift_features": summary.get("high_drift_features", []),
        "psi_summary": {
            "max_psi": summary.get("max_psi"),
            "drifted_feature_count": summary.get("drifted_feature_count"),
        },
        "score_distribution_shift": scorecard.get("fraud_score_distribution_shift"),
        "monitoring_summary_score": scorecard.get("monitoring_summary_score"),
    }


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
        "fraud_patterns": _json(get_path("scorecards") / "fraud_pattern_detection_report.json"),
        "data_quality": _json(get_path("scorecards") / "data_quality_detection_report.json"),
        "point_in_time": _json(get_path("scorecards") / "point_in_time_feature_validation.json"),
        "reason_codes": _json(get_path("scorecards") / "reason_code_report.json"),
        "alerts": _json(get_path("scorecards") / "alert_queue_quality_report.json"),
        "monitoring": _json(get_path("scorecards") / "model_monitoring_scorecard.json"),
    }


@app.get("/fraud-summary")
def fraud_summary() -> dict[str, object]:
    scored_path = get_path("scoring") / "scored_transactions.csv"
    alerts_path = get_path("alerts") / "fraud_alert_queue.csv"
    if not scored_path.exists():
        return {}
    scored = pd.read_csv(scored_path)
    alerts_df = pd.read_csv(alerts_path) if alerts_path.exists() else pd.DataFrame()
    registry = _json(get_path("model_registry") / "model_registry.json")
    reason_report = _json(get_path("scorecards") / "reason_code_report.json")
    drift_report = _json(get_path("scorecards") / "model_monitoring_scorecard.json")
    feature_report = _json(get_path("scorecards") / "feature_store_quality_report.json")
    model = _json(get_path("scorecards") / "fraud_model_scorecard.json")
    return {
        "total_transactions": int(len(scored)),
        "total_scored_transactions": int(len(scored)),
        "total_alerts": int(len(alerts_df)),
        "fraud_rate": round(float(scored["fraud_label"].astype(int).mean()), 4),
        "average_fraud_probability": round(float(scored["fraud_probability"].mean()), 4),
        "high_risk_count": int((scored["risk_band"] == "high").sum()),
        "critical_risk_count": int((scored["risk_band"] == "critical").sum()),
        "model_version": registry.get("model_version", "v0.2.0"),
        "top_reason_codes": reason_report.get("top_reason_codes", []),
        "drift_status": drift_report.get("overall_drift_status", "unknown"),
        "feature_store_quality_score": feature_report.get("overall_feature_store_quality_score"),
        "model_performance_summary": {
            "precision": model.get("precision"),
            "recall": model.get("recall"),
            "pr_auc": model.get("pr_auc"),
            "false_positive_rate": model.get("false_positive_rate"),
        },
    }
