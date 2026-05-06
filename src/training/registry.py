from __future__ import annotations

import json
from datetime import UTC, datetime

from src.common.config import get_path
from src.common.paths import ensure_directory


def write_registry(metrics: dict[str, object], model_path: str) -> dict[str, object]:
    """Write a lightweight model registry record."""
    registry = ensure_directory(get_path("model_registry"))
    record = {
        "model_name": "fraud_risk_random_forest",
        "model_version": "v0.1.0",
        "model_path": model_path,
        "registered_at": datetime.now(UTC).isoformat(),
        "metrics": metrics,
    }
    (registry / "model_registry.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record
