from __future__ import annotations

import numpy as np
import pandas as pd


def population_stability_index(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    """Calculate population stability index for a numeric feature."""
    expected = pd.to_numeric(expected, errors="coerce").dropna()
    actual = pd.to_numeric(actual, errors="coerce").dropna()
    if expected.empty or actual.empty:
        return 0.0
    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(expected, quantiles))
    if len(edges) < 3:
        return 0.0
    expected_counts = np.histogram(expected, bins=edges)[0] / max(1, len(expected))
    actual_counts = np.histogram(actual, bins=edges)[0] / max(1, len(actual))
    expected_counts = np.where(expected_counts == 0, 0.0001, expected_counts)
    actual_counts = np.where(actual_counts == 0, 0.0001, actual_counts)
    return round(float(np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))), 6)


def feature_drift_report(features: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Compare first half and second half feature distributions."""
    midpoint = len(features) // 2
    base = features.iloc[:midpoint]
    current = features.iloc[midpoint:]
    rows = []
    for col in columns:
        rows.append(
            {
                "feature_name": col,
                "population_stability_index": population_stability_index(base[col], current[col]),
                "mean_shift": round(float(current[col].mean() - base[col].mean()), 6),
                "missing_rate_change": round(float(current[col].isna().mean() - base[col].isna().mean()), 6),
                "category_distribution_shift": 0.0,
            }
        )
    return pd.DataFrame(rows)
