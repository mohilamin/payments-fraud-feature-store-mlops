from __future__ import annotations

import json

import pandas as pd

from src.common.config import get_path


def read_json(name: str) -> dict[str, object]:
    return json.loads((get_path("scorecards") / name).read_text())


def test_fraud_pattern_detection_report_creation(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "fraud_pattern_detection_report.json").exists()
    assert (get_path("scorecards") / "fraud_pattern_detection_report.csv").exists()


def test_fraud_pattern_detection_report_schema(pipeline_outputs: None) -> None:
    report = read_json("fraud_pattern_detection_report.json")
    assert {"total_injected_patterns", "detected_patterns", "detection_rate"}.issubset(report)


def test_fraud_pattern_detection_detail_schema(pipeline_outputs: None) -> None:
    detail = pd.read_csv(get_path("scorecards") / "fraud_pattern_detection_report.csv")
    assert {"pattern_type", "matched_transaction_count", "pass_fail"}.issubset(detail.columns)


def test_data_quality_detection_report_creation(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "data_quality_detection_report.json").exists()
    assert (get_path("scorecards") / "data_quality_detection_report.csv").exists()


def test_data_quality_detection_report_schema(pipeline_outputs: None) -> None:
    report = read_json("data_quality_detection_report.json")
    assert {"total_injected_issues", "detected_issues", "false_positive_count"}.issubset(report)


def test_data_quality_detection_detail_schema(pipeline_outputs: None) -> None:
    detail = pd.read_csv(get_path("scorecards") / "data_quality_detection_report.csv")
    assert {"issue_type", "matched_record_count", "missed_record_count"}.issubset(detail.columns)


def test_point_in_time_feature_validation_report_creation(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "point_in_time_feature_validation.json").exists()
    assert (get_path("scorecards") / "point_in_time_feature_validation.csv").exists()


def test_point_in_time_validation_all_safe(pipeline_outputs: None) -> None:
    detail = pd.read_csv(get_path("scorecards") / "point_in_time_feature_validation.csv")
    assert detail["point_in_time_safe"].all()


def test_feature_store_quality_report_schema(pipeline_outputs: None) -> None:
    report = read_json("feature_store_quality_report.json")
    assert {"total_feature_rows", "total_features", "overall_feature_store_quality_score"}.issubset(report)


def test_feature_store_group_quality_scores(pipeline_outputs: None) -> None:
    report = read_json("feature_store_quality_report.json")
    assert {"customer", "merchant", "device", "velocity", "transaction"}.issubset(
        report["feature_group_quality_score"]
    )


def test_model_scorecard_schema(pipeline_outputs: None) -> None:
    report = read_json("fraud_model_scorecard.json")
    assert {"model_name", "training_rows", "test_rows", "top_features_by_importance"}.issubset(report)


def test_model_registry_required_fields(pipeline_outputs: None) -> None:
    registry = json.loads((get_path("model_registry") / "model_registry.json").read_text())
    assert {"model_id", "model_version", "approved_for_demo_scoring", "intended_use"}.issubset(registry)


def test_reason_code_report_creation(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "reason_code_report.json").exists()
    assert (get_path("scorecards") / "reason_code_report.csv").exists()


def test_reason_code_coverage(pipeline_outputs: None) -> None:
    report = read_json("reason_code_report.json")
    assert report["reason_code_coverage_rate"] >= 0
    assert "HIGH_VELOCITY_CUSTOMER" in report["reason_code_catalog"]


def test_alert_queue_quality_report_creation(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "alert_queue_quality_report.json").exists()
    assert (get_path("scorecards") / "alert_queue_quality_report.csv").exists()


def test_alert_queue_quality_report_schema(pipeline_outputs: None) -> None:
    report = read_json("alert_queue_quality_report.json")
    assert {"total_alerts", "alert_precision_estimate", "alert_queue_quality_score"}.issubset(report)


def test_model_monitoring_scorecard_creation(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "model_monitoring_scorecard.json").exists()
    assert (get_path("scorecards") / "model_monitoring_scorecard.csv").exists()


def test_model_monitoring_scorecard_schema(pipeline_outputs: None) -> None:
    report = read_json("model_monitoring_scorecard.json")
    assert {"overall_drift_status", "monitoring_summary_score", "psi_by_feature"}.issubset(report)


def test_risk_band_distribution_in_model_scorecard(pipeline_outputs: None) -> None:
    report = read_json("fraud_model_scorecard.json")
    assert isinstance(report["risk_band_distribution"], dict)


def test_batch_scoring_output_schema(pipeline_outputs: None) -> None:
    scored = pd.read_csv(get_path("scoring") / "scored_transactions.csv")
    assert {"transaction_id", "fraud_probability", "risk_band", "top_reason_codes"}.issubset(scored.columns)


def test_alert_queue_output_schema(pipeline_outputs: None) -> None:
    alerts = pd.read_csv(get_path("alerts") / "fraud_alert_queue.csv")
    assert {"alert_id", "risk_band", "recommended_action", "investigator_priority"}.issubset(alerts.columns)


def test_end_to_end_output_files(pipeline_outputs: None) -> None:
    outputs = [
        get_path("scorecards") / "fraud_pattern_detection_report.json",
        get_path("scorecards") / "data_quality_detection_report.json",
        get_path("scorecards") / "point_in_time_feature_validation.json",
        get_path("scorecards") / "reason_code_report.json",
        get_path("scorecards") / "alert_queue_quality_report.json",
        get_path("scorecards") / "model_monitoring_scorecard.json",
    ]
    assert all(path.exists() for path in outputs)
