from __future__ import annotations

import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.common.config import get_path, get_settings
from src.common.paths import ROOT, ensure_directory
from src.scoring.reason_codes import risk_band
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
    threshold = float(get_settings()["scoring"]["threshold"])
    metrics = evaluate_predictions(y_test, y_prob, threshold)
    importances = sorted(
        zip(cols, model.feature_importances_, strict=False),
        key=lambda item: item[1],
        reverse=True,
    )[:10]
    metrics.update(
        {
            "model_name": "fraud_risk_random_forest",
            "model_version": "v0.2.0",
            "training_rows": int(len(x_train)),
            "test_rows": int(len(x_test)),
            "fraud_rate_train": round(float(y_train.mean()), 4),
            "fraud_rate_test": round(float(y_test.mean()), 4),
            "threshold_used": threshold,
            "risk_band_distribution": pd.Series(y_prob).map(risk_band).value_counts().to_dict(),
            "top_features_by_importance": [
                {"feature_name": name, "importance": round(float(value), 6)}
                for name, value in importances
            ],
            "model_artifact_path": str(get_path("model_artifacts") / "fraud_model.joblib"),
            "training_timestamp": pd.Timestamp.utcnow().isoformat(),
            "evaluation_interpretation": {
                "precision": "Precision estimates how many flagged transactions are truly fraud, which affects investigator workload and customer friction.",
                "recall": "Recall estimates how much known fraud is captured by the model.",
                "pr_auc": "PR AUC is useful for imbalanced fraud data because it focuses on precision-recall tradeoffs.",
                "false_positive_rate": "False positive rate estimates how often legitimate customers could be challenged or delayed.",
            },
        }
    )
    artifacts = ensure_directory(get_path("model_artifacts"))
    model_path = artifacts / "fraud_model.joblib"
    joblib.dump({"model": model, "feature_columns": cols}, model_path)
    write_registry(metrics, str(model_path), get_settings()["scoring"])
    scorecards = ensure_directory(get_path("scorecards"))
    pd.DataFrame([metrics]).to_csv(scorecards / "fraud_model_scorecard.csv", index=False)
    (scorecards / "fraud_model_scorecard.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _write_model_card(metrics)
    return {"model": model, "metrics": metrics, "feature_columns": cols}


def _write_model_card(metrics: dict[str, object]) -> None:
    card = (
        "# Model Card\n\n"
        "## Business Objective\n\n"
        "Score synthetic payment transactions for fraud risk using trusted point-in-time features, explainable reason codes, and monitoring evidence.\n\n"
        "## Model Type\n\n"
        "RandomForestClassifier deterministic baseline trained with scikit-learn.\n\n"
        "## Training Data\n\n"
        "Synthetic customers, accounts, merchants, devices, transactions, chargebacks, and fraud labels generated locally. No real payment or personal data is used.\n\n"
        "## Feature Groups\n\n"
        "Customer velocity, merchant risk, device risk, transaction context, and point-in-time behavioral aggregates.\n\n"
        "## Target Label\n\n"
        "`fraud_label`, a deterministic synthetic label produced during fraud pattern injection.\n\n"
        "## Threshold Strategy\n\n"
        "V0.2 uses a 0.50 prediction threshold and probability-based risk bands: low, medium, high, and critical.\n\n"
        "## Reason-Code Approach\n\n"
        "Reason codes are deterministic rule explanations mapped from engineered features, not SHAP. They are intended for portfolio demo transparency.\n\n"
        "## Metrics\n\n"
        f"```json\n{json.dumps(metrics, indent=2)}\n```\n\n"
        "## Ethical / Risk Considerations\n\n"
        "This model must not be used for real financial decisions. It is synthetic, locally generated, and designed only to demonstrate engineering workflow.\n\n"
        "## Monitoring Plan\n\n"
        "Monitor feature drift, score distribution shift, alert quality, and model performance when labels are available.\n\n"
        "## Future Enhancements\n\n"
        "MLflow tracking, Feast feature serving, SHAP explanations, streaming inference, cloud deployment, and human review workflows.\n"
    )
    (ensure_directory(ROOT / "docs") / "model-card.md").write_text(card, encoding="utf-8")


if __name__ == "__main__":
    train_model()
