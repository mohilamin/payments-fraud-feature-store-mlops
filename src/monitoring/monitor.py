from __future__ import annotations

import json

import pandas as pd

from src.common.config import get_path
from src.common.paths import ensure_directory
from src.monitoring.drift import feature_drift_report
from src.monitoring.performance import current_performance
from src.training.dataset import feature_columns


def run_monitoring(features: pd.DataFrame | None = None, scored: pd.DataFrame | None = None) -> dict[str, object]:
    """Write deterministic drift, scoring distribution, and performance reports."""
    features = features if features is not None else pd.read_csv(get_path("features") / "transaction_features.csv")
    scored = scored if scored is not None else pd.read_csv(get_path("scoring") / "scored_transactions.csv")
    output = ensure_directory(get_path("monitoring"))
    drift = feature_drift_report(features, feature_columns())
    drift.to_csv(output / "feature_drift_report.csv", index=False)
    summary = {
        "feature_count": int(len(drift)),
        "max_psi": float(drift["population_stability_index"].max()),
        "drifted_feature_count": int((drift["population_stability_index"] >= 0.10).sum()),
    }
    (output / "feature_drift_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    distribution = scored["risk_band"].value_counts(normalize=True).rename_axis("risk_band").reset_index(name="share")
    distribution.to_csv(output / "scoring_distribution_report.csv", index=False)
    performance = current_performance(scored)
    (output / "model_performance_report.json").write_text(
        json.dumps(performance, indent=2),
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    run_monitoring()
