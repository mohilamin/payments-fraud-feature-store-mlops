from __future__ import annotations

import json

import pandas as pd

from src.common.config import get_path
from src.monitoring.drift import population_stability_index
from src.scoring.reason_codes import generate_reason_codes, risk_band
from src.scoring.score_transaction import score_transaction


def test_model_training(pipeline_outputs: None) -> None:
    scorecard = json.loads((get_path("scorecards") / "fraud_model_scorecard.json").read_text())
    assert "roc_auc" in scorecard


def test_model_registry_creation(pipeline_outputs: None) -> None:
    assert (get_path("model_registry") / "model_registry.json").exists()


def test_batch_scoring(pipeline_outputs: None) -> None:
    scored = pd.read_csv(get_path("scoring") / "scored_transactions.csv")
    assert "fraud_probability" in scored.columns


def test_single_transaction_scoring(pipeline_outputs: None) -> None:
    result = score_transaction({"transaction_id": "unit", "amount": 900, "customer_txn_count_1h": 8})
    assert "fraud_probability" in result


def test_reason_code_generation() -> None:
    codes = generate_reason_codes({"customer_txn_count_1h": 8, "international_mismatch_flag": 1})
    assert "HIGH_VELOCITY_CUSTOMER" in codes


def test_risk_band_assignment() -> None:
    assert risk_band(0.9) == "critical"
    assert risk_band(0.1) == "low"


def test_alert_queue_creation(pipeline_outputs: None) -> None:
    assert (get_path("alerts") / "fraud_alert_queue.csv").exists()


def test_psi_calculation() -> None:
    psi = population_stability_index(pd.Series([1, 2, 3, 4]), pd.Series([1, 2, 8, 9]))
    assert psi >= 0


def test_psi_empty_series_edge_case() -> None:
    assert population_stability_index(pd.Series([], dtype=float), pd.Series([1, 2, 3])) == 0.0


def test_psi_constant_series_edge_case() -> None:
    assert population_stability_index(pd.Series([1, 1, 1]), pd.Series([1, 1, 1])) == 0.0


def test_drift_report_creation(pipeline_outputs: None) -> None:
    assert (get_path("monitoring") / "feature_drift_report.csv").exists()


def test_monitoring_summary(pipeline_outputs: None) -> None:
    summary = json.loads((get_path("monitoring") / "feature_drift_summary.json").read_text())
    assert "max_psi" in summary


def test_scoring_quality_report(pipeline_outputs: None) -> None:
    report = json.loads((get_path("scorecards") / "scoring_quality_report.json").read_text())
    assert report["scored_transaction_count"] > 0
