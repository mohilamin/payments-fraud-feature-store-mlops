from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app
from src.common.config import get_path


def test_full_pipeline_execution(pipeline_outputs: None) -> None:
    assert (get_path("scorecards") / "fraud_model_scorecard.json").exists()


def test_api_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_score_transaction_endpoint(pipeline_outputs: None) -> None:
    client = TestClient(app)
    response = client.post("/score-transaction", json={"transaction_id": "api", "amount": 1000})
    assert response.status_code == 200
    assert "risk_band" in response.json()


def test_api_fraud_summary_endpoint(pipeline_outputs: None) -> None:
    client = TestClient(app)
    response = client.get("/fraud-summary")
    assert response.status_code == 200
    assert "total_scored_transactions" in response.json()


def test_api_scorecards_endpoint(pipeline_outputs: None) -> None:
    client = TestClient(app)
    response = client.get("/scorecards")
    assert response.status_code == 200
    assert "model" in response.json()


def test_api_fraud_summary_schema(pipeline_outputs: None) -> None:
    client = TestClient(app)
    payload = client.get("/fraud-summary").json()
    assert {"model_version", "top_reason_codes", "drift_status", "feature_store_quality_score"}.issubset(payload)


def test_api_model_card_schema(pipeline_outputs: None) -> None:
    client = TestClient(app)
    payload = client.get("/model-card").json()
    assert {"model_name", "model_version", "metrics", "intended_use", "limitations"}.issubset(payload)


def test_api_drift_schema(pipeline_outputs: None) -> None:
    client = TestClient(app)
    payload = client.get("/monitoring/drift").json()
    assert {"overall_drift_status", "psi_summary", "monitoring_summary_score"}.issubset(payload)


def test_api_features_schema(pipeline_outputs: None) -> None:
    client = TestClient(app)
    payload = client.get("/features").json()
    assert {"feature_groups", "row_count", "quality_score", "sample_rows"}.issubset(payload)


def test_api_score_transaction_schema(pipeline_outputs: None) -> None:
    client = TestClient(app)
    payload = client.post("/score-transaction", json={"transaction_id": "schema", "amount": 1000}).json()
    assert {"model_version", "scoring_timestamp", "recommended_action", "reason_code_descriptions"}.issubset(payload)
