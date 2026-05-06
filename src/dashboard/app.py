from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.common.config import get_path
from src.scoring.score_transaction import score_transaction


def read_csv(path: Path) -> pd.DataFrame:
    """Read dashboard CSV safely."""
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def read_json(path: Path) -> dict[str, object]:
    """Read dashboard JSON safely."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    st.set_page_config(page_title="Fraud Feature Store + MLOps", layout="wide")
    st.title("Payments Fraud Feature Store + MLOps Pipeline")
    scorecard_path = get_path("scorecards")
    model = read_json(scorecard_path / "fraud_model_scorecard.json")
    feature_quality = read_json(scorecard_path / "feature_store_quality_report.json")
    scoring_quality = read_json(scorecard_path / "scoring_quality_report.json")
    pattern_report = read_json(scorecard_path / "fraud_pattern_detection_report.json")
    dq_report = read_json(scorecard_path / "data_quality_detection_report.json")
    pit_report = read_json(scorecard_path / "point_in_time_feature_validation.json")
    reason_report = read_json(scorecard_path / "reason_code_report.json")
    alert_quality = read_json(scorecard_path / "alert_queue_quality_report.json")
    monitoring_scorecard = read_json(scorecard_path / "model_monitoring_scorecard.json")
    drift = read_json(get_path("monitoring") / "feature_drift_summary.json")
    alerts = read_csv(get_path("alerts") / "fraud_alert_queue.csv")
    issues = read_csv(get_path("processed") / "data_quality_issues.csv")
    scored = read_csv(get_path("scoring") / "scored_transactions.csv")

    st.header("Executive Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precision", model.get("precision", "Run pipeline"))
    c2.metric("Recall", model.get("recall", "Run pipeline"))
    c3.metric("Alerts", alert_quality.get("total_alerts", scoring_quality.get("alert_count", len(alerts))))
    c4.metric("Feature Quality", feature_quality.get("overall_feature_store_quality_score", "Run pipeline"))

    st.header("Fraud Model Performance")
    st.json(model)

    st.header("Feature Store Overview")
    st.json(feature_quality)

    st.header("Fraud Pattern Detection")
    st.json(
        {
            "detection_rate": pattern_report.get("detection_rate"),
            "detected_patterns": pattern_report.get("detected_patterns"),
            "missed_patterns": pattern_report.get("missed_patterns"),
        }
    )
    st.dataframe(read_csv(scorecard_path / "fraud_pattern_detection_report.csv"), use_container_width=True)

    st.header("Data Quality Detection")
    st.json(
        {
            "detection_rate": dq_report.get("detection_rate"),
            "false_positive_count": dq_report.get("false_positive_count"),
        }
    )
    st.dataframe(read_csv(scorecard_path / "data_quality_detection_report.csv"), use_container_width=True)

    st.header("Point-in-Time Validation")
    st.json({"pass_rate": pit_report.get("pass_rate"), "passed_checks": pit_report.get("passed_checks")})
    st.dataframe(read_csv(scorecard_path / "point_in_time_feature_validation.csv"), use_container_width=True)

    st.header("Fraud Alerts")
    st.dataframe(alerts.head(200), use_container_width=True)

    st.header("Transaction Scoring Lab")
    amount = st.number_input("Amount", value=750.0)
    high_velocity = st.checkbox("High velocity")
    if st.button("Score Transaction"):
        payload = {"transaction_id": "demo", "amount": amount, "customer_txn_count_1h": 7 if high_velocity else 0}
        st.json(score_transaction(payload))

    st.header("Reason Code Explorer")
    st.json(
        {
            "coverage_rate": reason_report.get("reason_code_coverage_rate"),
            "top_reason_codes": reason_report.get("top_reason_codes"),
        }
    )
    if not scored.empty:
        st.dataframe(scored[["transaction_id", "risk_band", "top_reason_codes", "recommended_action"]].head(100), use_container_width=True)

    st.header("Alert Queue Quality")
    st.json(alert_quality)

    st.header("Drift Monitoring")
    st.json({"drift": drift, "monitoring_scorecard": monitoring_scorecard})
    st.dataframe(read_csv(get_path("monitoring") / "feature_drift_report.csv"), use_container_width=True)

    st.header("Data Quality Issues")
    st.dataframe(issues.head(200), use_container_width=True)

    st.header("Model Card")
    card = Path("docs/model-card.md")
    st.markdown(card.read_text(encoding="utf-8") if card.exists() else "Run pipeline to generate model card.")

    st.header("Investigator Queue")
    st.dataframe(alerts.sort_values("investigator_priority").head(200) if not alerts.empty else alerts, use_container_width=True)


if __name__ == "__main__":
    main()
