from __future__ import annotations

import joblib
import pandas as pd

from src.common.config import get_path
from src.scoring.reason_codes import (
    descriptions,
    generate_reason_codes,
    recommended_action,
    risk_band,
)
from src.training.dataset import feature_columns


def score_transaction(transaction: dict[str, object]) -> dict[str, object]:
    """Score a single already-featured transaction payload."""
    frame = pd.DataFrame([transaction])
    cols = feature_columns()
    for col in cols:
        if col not in frame.columns:
            frame[col] = 0
    artifact = joblib.load(get_path("model_artifacts") / "fraud_model.joblib")
    probability = float(artifact["model"].predict_proba(frame[cols].fillna(0))[:, 1][0])
    prediction = int(probability >= 0.5)
    row = frame.iloc[0].to_dict()
    row["fraud_probability"] = probability
    codes = generate_reason_codes(row)
    band = risk_band(probability)
    return {
        "transaction_id": row.get("transaction_id", "ad_hoc"),
        "fraud_probability": probability,
        "fraud_prediction": prediction,
        "risk_band": band,
        "top_reason_codes": codes,
        "reason_code_descriptions": descriptions(codes),
        "recommended_action": recommended_action(band),
        "feature_count": len(feature_columns()),
    }
