from __future__ import annotations

import pandas as pd


def prior_window_count(frame: pd.DataFrame, entity_col: str, window: str) -> pd.Series:
    """Count prior entity events within a time window."""
    return _rolling(frame, entity_col, window, "count")


def prior_window_sum(frame: pd.DataFrame, entity_col: str, value_col: str, window: str) -> pd.Series:
    """Sum prior entity values within a time window."""
    return _rolling(frame, entity_col, window, "sum", value_col)


def _rolling(
    frame: pd.DataFrame,
    entity_col: str,
    window: str,
    op: str,
    value_col: str = "transaction_id",
) -> pd.Series:
    values = pd.Series(0.0, index=frame.index)
    for _, group in frame.groupby(entity_col, sort=False):
        ordered = group.sort_values("transaction_timestamp")
        indexed = ordered.set_index("transaction_timestamp")
        series = indexed[value_col]
        if op == "count":
            rolled = series.rolling(window, closed="left").count()
        else:
            rolled = pd.to_numeric(series, errors="coerce").rolling(window, closed="left").sum()
        values.loc[ordered.index] = rolled.fillna(0).to_numpy()
    return values
