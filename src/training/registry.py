from __future__ import annotations

import json
from datetime import UTC, datetime

from src.common.config import get_path
from src.common.paths import ensure_directory


def write_registry(metrics: dict[str, object], model_path: str, thresholds: dict[str, object]) -> dict[str, object]:
    """Write a lightweight model registry record."""
    registry = ensure_directory(get_path("model_registry"))
    record = {
        "model_id": "fraud-rf-v0-2-demo",
        "model_name": "fraud_risk_random_forest",
        "model_version": "v0.2.0",
        "model_type": "RandomForestClassifier",
        "training_data_version": "synthetic_payments_v0.2",
        "feature_store_version": "duckdb_offline_v0.2",
        "training_timestamp": datetime.now(UTC).isoformat(),
        "metrics": metrics,
        "thresholds": thresholds,
        "artifact_path": model_path,
        "approved_for_demo_scoring": True,
        "known_limitations": [
            "Synthetic data only",
            "No real payment, card, customer, merchant, or bank data",
            "Deterministic local baseline, not a production fraud model",
        ],
        "intended_use": "Local portfolio demo for fraud feature engineering, scoring, and monitoring workflows.",
        "not_intended_use": "Real fraud decisions, customer friction decisions, credit decisions, or compliance operations.",
    }
    (registry / "model_registry.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record
