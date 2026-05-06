from __future__ import annotations

import json

import duckdb
import pandas as pd

from src.common.config import get_path
from src.data_generation.generate_synthetic_payments import generate_synthetic_payments
from src.features.customer_features import build_customer_features
from src.features.device_features import build_device_features
from src.features.merchant_features import build_merchant_features
from src.ingestion.loaders import load_raw_data
from src.quality.checks import detect_quality_issues


def test_synthetic_data_generation() -> None:
    generate_synthetic_payments()
    assert (get_path("raw") / "payment_transactions.csv").exists()
    assert len(pd.read_csv(get_path("raw") / "payment_transactions.csv")) >= 50000


def test_fraud_pattern_manifest_creation() -> None:
    generate_synthetic_payments()
    manifest = json.loads((get_path("raw") / "injected_fraud_pattern_manifest.json").read_text())
    assert len(manifest["patterns"]) >= 12


def test_data_quality_manifest_creation() -> None:
    generate_synthetic_payments()
    manifest = json.loads((get_path("raw") / "injected_data_quality_manifest.json").read_text())
    assert len(manifest["issues"]) >= 10


def test_ingestion() -> None:
    generate_synthetic_payments()
    frames = load_raw_data()
    assert "payment_transactions" in frames
    assert "customers" in frames


def test_data_quality_validation() -> None:
    generate_synthetic_payments()
    issues = detect_quality_issues(load_raw_data())
    assert {"missing_customer_id", "invalid_merchant_id", "negative_transaction_amount"}.issubset(
        set(issues["issue_type"])
    )


def test_quarantine_output(pipeline_outputs: None) -> None:
    assert (get_path("processed") / "quarantine" / "payment_transactions_quarantine.csv").exists()


def test_point_in_time_feature_correctness() -> None:
    frame = pd.DataFrame(
        {
            "transaction_id": ["t1", "t2"],
            "customer_id": ["c1", "c1"],
            "merchant_id": ["m1", "m2"],
            "merchant_country": ["US", "US"],
            "auth_result": ["approved", "approved"],
            "transaction_timestamp": pd.to_datetime(["2025-01-01T00:00:00", "2025-01-01T00:30:00"]),
            "amount": [10.0, 20.0],
        }
    )
    features = build_customer_features(frame)
    assert features.loc[features["transaction_id"] == "t1", "customer_txn_count_1h"].iloc[0] == 0
    assert features.loc[features["transaction_id"] == "t2", "customer_txn_count_1h"].iloc[0] == 1


def test_customer_velocity_features(pipeline_outputs: None) -> None:
    features = pd.read_csv(get_path("features") / "transaction_features.csv")
    assert "customer_txn_count_24h" in features.columns


def test_merchant_risk_features(pipeline_outputs: None) -> None:
    features = pd.read_csv(get_path("features") / "transaction_features.csv")
    assert "merchant_risk_score" in features.columns


def test_device_features(pipeline_outputs: None) -> None:
    features = pd.read_csv(get_path("features") / "transaction_features.csv")
    assert "device_risk_score" in features.columns


def test_feature_store_creation(pipeline_outputs: None) -> None:
    db = get_path("features") / "fraud_feature_store.duckdb"
    assert db.exists()
    with duckdb.connect(str(db)) as connection:
        count = connection.execute("SELECT count(*) FROM transaction_features").fetchone()[0]
    assert count > 0


def test_training_dataset_creation(pipeline_outputs: None) -> None:
    assert (get_path("training") / "training_dataset.csv").exists()


def test_feature_builder_functions_are_callable() -> None:
    assert callable(build_merchant_features)
    assert callable(build_device_features)
