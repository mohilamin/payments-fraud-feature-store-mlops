from __future__ import annotations

import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.common.config import get_path, get_settings
from src.common.paths import ROOT, ensure_directory
from src.training.dataset import build_training_dataset, feature_columns, load_feature_table
from src.training.evaluate_model import evaluate_predictions
from src.training.registry import write_registry


def train_model(features: pd.DataFrame | None = None) -> dict[str, object]:
    """Train deterministic baseline fraud model and write artifacts."""
    features = features if features is not None else load_feature_table()
    dataset = build_training_dataset(features)
    cols = feature_columns()
    x = dataset[cols].fillna(0)
    y = dataset["fraud_label"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=float(get_settings()["training"]["test_size"]),
        random_state=int(get_settings()["random_seed"]),
        stratify=y,
    )
    model = RandomForestClassifier(
        n_estimators=80,
        max_depth=10,
        min_samples_leaf=20,
        class_weight="balanced",
        random_state=int(get_settings()["random_seed"]),
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    y_prob = model.predict_proba(x_test)[:, 1]
    metrics = evaluate_predictions(y_test, y_prob, float(get_settings()["scoring"]["threshold"]))
    artifacts = ensure_directory(get_path("model_artifacts"))
    model_path = artifacts / "fraud_model.joblib"
    joblib.dump({"model": model, "feature_columns": cols}, model_path)
    write_registry(metrics, str(model_path))
    scorecards = ensure_directory(get_path("scorecards"))
    pd.DataFrame([metrics]).to_csv(scorecards / "fraud_model_scorecard.csv", index=False)
    (scorecards / "fraud_model_scorecard.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _write_model_card(metrics)
    return {"model": model, "metrics": metrics, "feature_columns": cols}


def _write_model_card(metrics: dict[str, object]) -> None:
    card = (
        "# Model Card\n\n"
        "Model: RandomForestClassifier baseline for synthetic payment fraud.\n\n"
        "Purpose: score synthetic payment transactions for fraud risk using point-in-time features.\n\n"
        "Limitations: synthetic data only, deterministic baseline, no SHAP or production monitoring service.\n\n"
        f"Metrics:\n\n```json\n{json.dumps(metrics, indent=2)}\n```\n"
    )
    (ensure_directory(ROOT / "docs") / "model-card.md").write_text(card, encoding="utf-8")


if __name__ == "__main__":
    train_model()
