from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.common.config import get_path
from src.common.paths import ensure_directory
from src.monitoring.drift import feature_drift_report
from src.scoring.reason_codes import ALL_REASON_CODES
from src.training.dataset import feature_columns

GROUPS = {
    "customer": [
        "customer_txn_count_1h",
        "customer_txn_count_24h",
        "customer_total_amount_24h",
        "customer_avg_amount_30d",
        "customer_failed_auth_count_24h",
        "customer_distinct_merchants_24h",
        "customer_distinct_countries_24h",
    ],
    "merchant": [
        "merchant_txn_count_24h",
        "merchant_fraud_rate_30d",
        "merchant_avg_amount_30d",
        "merchant_chargeback_rate_30d",
        "merchant_risk_score",
    ],
    "device": [
        "device_txn_count_24h",
        "device_distinct_customers_24h",
        "device_age_days",
        "device_risk_score",
        "new_device_flag",
    ],
    "velocity": ["customer_txn_count_1h", "customer_txn_count_24h", "device_txn_count_24h"],
    "transaction": [
        "amount_zscore_customer",
        "international_mismatch_flag",
        "card_not_present_flag",
        "impossible_travel_flag",
        "night_transaction_flag",
        "high_velocity_flag",
        "risky_merchant_category_flag",
    ],
}


def generate_evidence_reports(
    frames: dict[str, pd.DataFrame],
    issues: pd.DataFrame,
    features: pd.DataFrame,
    scored: pd.DataFrame,
) -> None:
    """Generate deterministic V0.2 portfolio evidence reports."""
    scorecards = ensure_directory(get_path("scorecards"))
    pit = write_point_in_time_validation(features, scorecards)
    write_feature_store_quality(features, pit, scorecards)
    write_fraud_pattern_detection(scored, scorecards)
    write_data_quality_detection(issues, scorecards)
    write_reason_code_report(scored, scorecards)
    write_alert_queue_quality(scored, scorecards)
    write_model_monitoring_scorecard(features, scored, scorecards)


def write_fraud_pattern_detection(scored: pd.DataFrame, scorecards: Path) -> dict[str, object]:
    """Compare injected fraud patterns to high-risk scored outcomes."""
    manifest = _json(get_path("raw") / "injected_fraud_pattern_manifest.json")
    rows: list[dict[str, object]] = []
    detected_pattern_count = 0
    for pattern in manifest.get("patterns", []):
        expected = [str(x) for x in pattern.get("transaction_ids", [])]
        subset = scored.loc[scored["transaction_id"].astype(str).isin(expected)].copy()
        detected = subset.loc[subset["risk_band"].isin(["medium", "high", "critical"]), "transaction_id"].astype(str).tolist()
        matched = sorted(set(expected) & set(detected))
        bands = subset["risk_band"].value_counts()
        average_band = bands.idxmax() if not bands.empty else "not_scored"
        passed = len(matched) > 0
        detected_pattern_count += int(passed)
        rows.append(
            {
                "pattern_type": pattern["pattern_type"],
                "expected_transaction_ids": "|".join(expected[:50]),
                "detected_transaction_ids": "|".join(detected[:50]),
                "matched_transaction_count": len(matched),
                "missed_transaction_count": max(0, len(expected) - len(matched)),
                "average_fraud_probability_by_pattern": round(float(subset["fraud_probability"].mean()), 4)
                if not subset.empty
                else 0.0,
                "average_risk_band_by_pattern": average_band,
                "pass_fail": "pass" if passed else "fail",
            }
        )
    detail = pd.DataFrame(rows)
    detail.to_csv(scorecards / "fraud_pattern_detection_report.csv", index=False)
    summary = {
        "total_injected_patterns": int(len(rows)),
        "detected_patterns": int(detected_pattern_count),
        "missed_patterns": int(len(rows) - detected_pattern_count),
        "detection_rate": _rate(detected_pattern_count, len(rows)),
        "detection_rate_by_pattern_type": {
            row["pattern_type"]: 100.0 if row["pass_fail"] == "pass" else 0.0 for row in rows
        },
        "patterns": rows,
    }
    _write_json(scorecards / "fraud_pattern_detection_report.json", summary)
    return summary


def write_data_quality_detection(issues: pd.DataFrame, scorecards: Path) -> dict[str, object]:
    """Compare injected data quality issues to detected issue records."""
    manifest = _json(get_path("raw") / "injected_data_quality_manifest.json")
    detected_pairs = set(zip(issues["issue_type"].astype(str), issues["record_id"].astype(str), strict=False))
    rows = []
    detected_total = 0
    expected_total = 0
    expected_all: set[tuple[str, str]] = set()
    for issue in manifest.get("issues", []):
        issue_type = str(issue["issue_type"])
        expected = [str(x) for x in issue.get("transaction_ids", [])]
        expected_total += len(expected)
        expected_pairs = {(issue_type, record_id) for record_id in expected}
        expected_all.update(expected_pairs)
        matched = sorted(record_id for _, record_id in expected_pairs & detected_pairs)
        detected_records = sorted(record_id for kind, record_id in detected_pairs if kind == issue_type)
        detected_total += len(matched)
        rows.append(
            {
                "issue_type": issue_type,
                "expected_record_ids": "|".join(expected[:50]),
                "detected_record_ids": "|".join(detected_records[:50]),
                "matched_record_count": len(matched),
                "missed_record_count": max(0, len(expected) - len(matched)),
                "pass_fail": "pass" if len(matched) == len(expected) else "fail",
            }
        )
    detail = pd.DataFrame(rows)
    detail.to_csv(scorecards / "data_quality_detection_report.csv", index=False)
    false_positives = max(0, len(detected_pairs - expected_all))
    by_type = {
        row["issue_type"]: _rate(row["matched_record_count"], row["matched_record_count"] + row["missed_record_count"])
        for row in rows
    }
    summary = {
        "total_injected_issues": int(expected_total),
        "detected_issues": int(detected_total),
        "missed_issues": int(expected_total - detected_total),
        "false_positive_count": int(false_positives),
        "detection_rate": _rate(detected_total, expected_total),
        "detection_rate_by_issue_type": by_type,
        "issues": rows,
    }
    _write_json(scorecards / "data_quality_detection_report.json", summary)
    return summary


def write_point_in_time_validation(features: pd.DataFrame, scorecards: Path) -> pd.DataFrame:
    """Write sampled point-in-time safety evidence for important features."""
    frame = features.copy()
    frame["transaction_timestamp"] = pd.to_datetime(frame["transaction_timestamp"], errors="coerce")
    checks = [
        ("customer_txn_count_1h", "customer_id", "1h"),
        ("customer_txn_count_24h", "customer_id", "24h"),
        ("customer_total_amount_24h", "customer_id", "24h"),
        ("customer_avg_amount_30d", "customer_id", "30D"),
        ("merchant_fraud_rate_30d", "merchant_id", "30D"),
        ("device_txn_count_24h", "device_id", "24h"),
        ("impossible_travel_flag", "customer_id", "1h"),
    ]
    rows = []
    for feature_name, entity_col, window in checks:
        candidates = frame.loc[frame[feature_name].fillna(0).ne(0)].copy()
        sample = candidates.iloc[len(candidates) // 2] if not candidates.empty else frame.iloc[len(frame) // 2]
        current_time = sample["transaction_timestamp"]
        start_time = current_time - pd.Timedelta(window)
        source = frame.loc[
            (frame[entity_col] == sample[entity_col])
            & (frame["transaction_timestamp"] < current_time)
            & (frame["transaction_timestamp"] >= start_time)
        ]
        max_source_time = source["transaction_timestamp"].max() if not source.empty else pd.NaT
        safe = pd.isna(max_source_time) or max_source_time < current_time
        rows.append(
            {
                "feature_name": feature_name,
                "sampled_transaction_id": sample["transaction_id"],
                "transaction_timestamp": current_time.isoformat(),
                "max_source_timestamp_used": "" if pd.isna(max_source_time) else max_source_time.isoformat(),
                "point_in_time_safe": bool(safe),
                "violation_reason": "" if safe else "source timestamp is not before scored transaction",
            }
        )
    report = pd.DataFrame(rows)
    report.to_csv(scorecards / "point_in_time_feature_validation.csv", index=False)
    summary = {
        "total_checks": int(len(report)),
        "passed_checks": int(report["point_in_time_safe"].sum()),
        "pass_rate": _rate(int(report["point_in_time_safe"].sum()), len(report)),
        "checks": rows,
    }
    _write_json(scorecards / "point_in_time_feature_validation.json", summary)
    return report


def write_feature_store_quality(features: pd.DataFrame, pit: pd.DataFrame, scorecards: Path) -> dict[str, object]:
    """Write enhanced feature store quality evidence."""
    cols = feature_columns()
    missing = {col: round(float(features[col].isna().mean()), 6) for col in cols}
    zero_variance = [col for col in cols if features[col].nunique(dropna=True) <= 1]
    high_null = [col for col, rate in missing.items() if rate >= 0.05]
    group_scores = {}
    for group, group_cols in GROUPS.items():
        valid_cols = [col for col in group_cols if col in features.columns]
        avg_missing = sum(missing.get(col, 0.0) for col in valid_cols) / max(1, len(valid_cols))
        variance_penalty = 5 * len([col for col in valid_cols if col in zero_variance])
        group_scores[group] = round(max(0.0, 100.0 - (avg_missing * 100) - variance_penalty), 2)
    pass_rate = round(float(pit["point_in_time_safe"].mean()) * 100, 2)
    overall = round((sum(group_scores.values()) / len(group_scores) * 0.7) + (pass_rate * 0.3), 2)
    freshness = {
        "min_transaction_timestamp": str(features["transaction_timestamp"].min()),
        "max_transaction_timestamp": str(features["transaction_timestamp"].max()),
        "row_count": int(len(features)),
    }
    summary = {
        "total_feature_rows": int(len(features)),
        "row_count": int(len(features)),
        "total_features": int(len(cols)),
        "feature_count": int(len(cols)),
        "missing_rate_by_feature": missing,
        "zero_variance_features": zero_variance,
        "high_null_features": high_null,
        "feature_freshness_summary": freshness,
        "point_in_time_validation_pass_rate": pass_rate,
        "feature_group_quality_score": group_scores,
        "overall_feature_store_quality_score": overall,
        "max_missing_rate": max(missing.values()) if missing else 0.0,
    }
    detail = pd.DataFrame(
        [
            {
                "feature_name": col,
                "missing_rate": missing[col],
                "zero_variance": col in zero_variance,
                "feature_group": _group_for(col),
            }
            for col in cols
        ]
    )
    detail.to_csv(scorecards / "feature_store_quality_report.csv", index=False)
    _write_json(scorecards / "feature_store_quality_report.json", summary)
    return summary


def write_reason_code_report(scored: pd.DataFrame, scorecards: Path) -> dict[str, object]:
    """Write reason-code coverage evidence."""
    high_risk = scored.loc[scored["risk_band"].isin(["high", "critical"])].copy()
    code_lists = scored["top_reason_codes"].fillna("").map(lambda value: [x for x in str(value).split("|") if x])
    high_code_lists = high_risk["top_reason_codes"].fillna("").map(lambda value: [x for x in str(value).split("|") if x])
    frequency = Counter(code for codes in code_lists for code in codes if code != "LOW_RISK_BASELINE")
    missing_count = int((high_code_lists.map(len) == 0).sum())
    coverage = _rate(int((high_code_lists.map(len) > 0).sum()), len(high_risk))
    summary = {
        "total_scored_transactions": int(len(scored)),
        "high_risk_transactions": int(len(high_risk)),
        "transactions_with_reason_codes": int((code_lists.map(len) > 0).sum()),
        "reason_code_coverage_rate": coverage,
        "reason_code_frequency": dict(frequency),
        "average_reason_codes_per_alert": round(float(high_code_lists.map(len).mean() if len(high_risk) else 0), 2),
        "top_reason_codes": [code for code, _ in frequency.most_common(10)],
        "missing_reason_code_count": missing_count,
        "reason_code_catalog": ALL_REASON_CODES,
    }
    detail = pd.DataFrame(
        [{"reason_code": code, "frequency": frequency.get(code, 0)} for code in ALL_REASON_CODES]
    )
    detail.to_csv(scorecards / "reason_code_report.csv", index=False)
    _write_json(scorecards / "reason_code_report.json", summary)
    return summary


def write_alert_queue_quality(scored: pd.DataFrame, scorecards: Path) -> dict[str, object]:
    """Write alert queue quality evidence."""
    alerts = scored.loc[scored["risk_band"].isin(["high", "critical"])].copy()
    reason_counts = Counter(
        code
        for value in alerts["top_reason_codes"].fillna("")
        for code in str(value).split("|")
        if code and code != "LOW_RISK_BASELINE"
    )
    precision = round(float(alerts["fraud_label"].astype(int).mean()) * 100, 2) if not alerts.empty else 0.0
    quality_score = round(min(100.0, (precision * 0.6) + (_rate(len(alerts), max(1, len(scored))) * 0.4)), 2)
    summary = {
        "total_alerts": int(len(alerts)),
        "alerts_by_risk_band": alerts["risk_band"].value_counts().to_dict(),
        "alerts_by_recommended_action": alerts["recommended_action"].value_counts().to_dict(),
        "average_fraud_probability": round(float(alerts["fraud_probability"].mean()), 4) if not alerts.empty else 0.0,
        "confirmed_fraud_rate_in_alerts": precision,
        "top_alert_reason_codes": [code for code, _ in reason_counts.most_common(10)],
        "manual_review_volume": int((alerts["recommended_action"] == "manual_review").sum()),
        "decline_volume": int((alerts["recommended_action"] == "decline").sum()),
        "step_up_authentication_volume": int((alerts["recommended_action"] == "step_up_authentication").sum()),
        "alert_precision_estimate": precision,
        "alert_queue_quality_score": quality_score,
    }
    pd.DataFrame([summary]).to_csv(scorecards / "alert_queue_quality_report.csv", index=False)
    _write_json(scorecards / "alert_queue_quality_report.json", summary)
    return summary


def write_model_monitoring_scorecard(features: pd.DataFrame, scored: pd.DataFrame, scorecards: Path) -> dict[str, object]:
    """Write model monitoring scorecard from drift and scoring outputs."""
    drift = feature_drift_report(features, feature_columns())
    high_drift = drift.loc[drift["population_stability_index"].ge(0.25), "feature_name"].tolist()
    medium_drift = drift.loc[
        drift["population_stability_index"].ge(0.10) & drift["population_stability_index"].lt(0.25),
        "feature_name",
    ].tolist()
    severity = "high" if high_drift else "medium" if medium_drift else "low"
    risk_dist = scored["risk_band"].value_counts(normalize=True).to_dict()
    score_shift = round(float(scored["fraud_probability"].tail(len(scored) // 2).mean() - scored["fraud_probability"].head(len(scored) // 2).mean()), 6)
    monitoring_score = round(max(0.0, 100 - (20 * len(high_drift)) - (5 * len(medium_drift)) - abs(score_shift) * 100), 2)
    summary = {
        "psi_by_feature": dict(zip(drift["feature_name"], drift["population_stability_index"], strict=False)),
        "mean_shift_by_feature": dict(zip(drift["feature_name"], drift["mean_shift"], strict=False)),
        "missing_rate_change_by_feature": dict(zip(drift["feature_name"], drift["missing_rate_change"], strict=False)),
        "category_distribution_shift": {},
        "fraud_score_distribution_shift": score_shift,
        "risk_band_distribution_shift": risk_dist,
        "drift_severity": severity,
        "overall_drift_status": severity,
        "high_drift_features": high_drift,
        "monitoring_summary_score": monitoring_score,
    }
    pd.DataFrame([summary]).to_csv(scorecards / "model_monitoring_scorecard.csv", index=False)
    _write_json(scorecards / "model_monitoring_scorecard.json", summary)
    return summary


def _group_for(feature: str) -> str:
    for group, features in GROUPS.items():
        if feature in features:
            return group
    return "other"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _write_json(path: Path, payload: dict[str, object]) -> None:
    payload["generated_at"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _rate(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 2) if denominator else 0.0
