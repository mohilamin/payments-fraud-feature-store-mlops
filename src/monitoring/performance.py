from __future__ import annotations

from src.training.evaluate_model import evaluate_predictions


def current_performance(scored):
    """Calculate performance from scored transactions with labels."""
    return evaluate_predictions(scored["fraud_label"].astype(int), scored["fraud_probability"])
