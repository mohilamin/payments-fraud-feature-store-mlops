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
    assert "scored_transactions" in response.json()


def test_api_scorecards_endpoint(pipeline_outputs: None) -> None:
    client = TestClient(app)
    response = client.get("/scorecards")
    assert response.status_code == 200
    assert "model" in response.json()
