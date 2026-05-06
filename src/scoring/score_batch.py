from __future__ import annotations

import json

import joblib
import pandas as pd

from src.common.config import get_path, get_settings
from src.common.paths import ensure_directory
from src.scoring.alert_queue import write_alert_queue
from src.scoring.reason_codes import (
    descriptions,
    generate_reason_codes,
    recommended_action,
    risk_band,
)
from src.training.dataset import feature_columns, load_feature_table


def score_batch(features: pd.DataFrame | None = None) -> pd.DataFrame:
    """Score the generated feature table."""
    features = features if features is not None else load_feature_table()
    artifact = joblib.load(get_path("model_artifacts") / "fraud_model.joblib")
    model = artifact["model"]
    cols = artifact.get("feature_columns", feature_columns())
    features = features.copy()
    for col in ["amount", "fraud_label", *cols]:
        if col not in features.columns:
            features[col] = 0
    probabilities = model.predict_proba(features[cols].fillna(0))[:, 1]
    output = features[["transaction_id", "amount", "fraud_label", *cols]].copy()
    output["fraud_probability"] = probabilities
    output["fraud_prediction"] = (output["fraud_probability"] >= float(get_settings()["scoring"]["threshold"])).astype(int)
    output["risk_band"] = output["fraud_probability"].map(risk_band)
    output["top_reason_codes"] = output.apply(lambda row: "|".join(generate_reason_codes(row.to_dict())), axis=1)
    output["reason_code_descriptions"] = output["top_reason_codes"].map(lambda value: "|".join(descriptions(value.split("|"))))
    output["recommended_action"] = output["risk_band"].map(recommended_action)
    ensure_directory(get_path("scoring"))
    output.to_csv(get_path("scoring") / "scored_transactions.csv", index=False)
    write_alert_queue(output)
    _write_quality(output)
    return output


def _write_quality(scored: pd.DataFrame) -> None:
    scorecards = ensure_directory(get_path("scorecards"))
    report = {
        "scored_transaction_count": int(len(scored)),
        "alert_count": int(scored["risk_band"].isin(["high", "critical"]).sum()),
        "average_fraud_probability": round(float(scored["fraud_probability"].mean()), 4),
        "missing_probability_count": int(scored["fraud_probability"].isna().sum()),
    }
    pd.DataFrame([report]).to_csv(scorecards / "scoring_quality_report.csv", index=False)
    (scorecards / "scoring_quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    score_batch()
