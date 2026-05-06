from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_predictions(y_true, y_prob, threshold: float = 0.5) -> dict[str, object]:
    """Calculate fraud model metrics."""
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fraud_total = max(1, int(np.sum(y_true)))
    tn, fp, _, _ = cm.ravel()
    return {
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4),
        "confusion_matrix": cm.tolist(),
        "fraud_capture_rate_top_1_percent": _top_capture(y_true, y_prob, 0.01, fraud_total),
        "fraud_capture_rate_top_5_percent": _top_capture(y_true, y_prob, 0.05, fraud_total),
        "fraud_capture_rate_top_10_percent": _top_capture(y_true, y_prob, 0.10, fraud_total),
        "false_positive_rate": round(float(fp / max(1, fp + tn)), 4),
    }


def _top_capture(y_true, y_prob, share: float, fraud_total: int) -> float:
    top_n = max(1, int(len(y_prob) * share))
    top_idx = np.argsort(y_prob)[-top_n:]
    return round(float(np.sum(y_true.iloc[top_idx]) / fraud_total), 4)
