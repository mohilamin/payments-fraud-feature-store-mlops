from __future__ import annotations

import pandas as pd

from src.common.config import get_path
from src.common.paths import ensure_directory


def write_alert_queue(scored: pd.DataFrame) -> pd.DataFrame:
    """Write investigator alert queue."""
    alerts = scored.loc[scored["risk_band"].isin(["high", "critical"])].copy()
    alerts["alert_id"] = [f"ALERT-{i:06d}" for i in range(len(alerts))]
    alerts["queue_status"] = "open"
    alerts["investigator_priority"] = alerts["risk_band"].map({"critical": 1, "high": 2})
    ensure_directory(get_path("alerts"))
    alerts.to_csv(get_path("alerts") / "fraud_alert_queue.csv", index=False)
    return alerts
