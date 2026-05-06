from __future__ import annotations

from src.common.config import get_path
from src.common.logging import get_logger
from src.common.paths import ensure_directory
from src.data_generation.generate_synthetic_payments import generate_synthetic_payments
from src.features.build_features import build_transaction_features
from src.ingestion.loaders import load_raw_data
from src.ingestion.validators import validate_required_columns
from src.monitoring.monitor import run_monitoring
from src.quality.checks import clean_transactions, detect_quality_issues
from src.quality.quarantine import write_quality_outputs
from src.scoring.score_batch import score_batch
from src.training.train_model import train_model

LOGGER = get_logger(__name__)


def run_pipeline() -> None:
    """Run the end-to-end local fraud feature store and MLOps pipeline."""
    for key in ["raw", "processed", "features", "training", "scoring", "alerts", "monitoring", "scorecards", "model_artifacts", "model_registry"]:
        ensure_directory(get_path(key))
    generate_synthetic_payments()
    frames = load_raw_data()
    validate_required_columns(frames)
    issues = detect_quality_issues(frames)
    write_quality_outputs(frames["payment_transactions"], issues)
    clean = clean_transactions(frames, issues)
    features = build_transaction_features(frames, clean)
    train_model(features)
    scored = score_batch(features)
    run_monitoring(features, scored)
    LOGGER.info("pipeline complete")


if __name__ == "__main__":
    run_pipeline()
