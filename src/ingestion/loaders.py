from __future__ import annotations

import pandas as pd

from src.common.config import get_path
from src.common.logging import get_logger

LOGGER = get_logger(__name__)

RAW_FILES = {
    "customers": "customers.csv",
    "accounts": "accounts.csv",
    "merchants": "merchants.csv",
    "devices": "devices.csv",
    "payment_transactions": "payment_transactions.csv",
    "chargebacks": "chargebacks.csv",
    "fraud_labels": "fraud_labels.csv",
    "merchant_risk_profiles": "merchant_risk_profiles.csv",
    "device_risk_profiles": "device_risk_profiles.csv",
}


def load_raw_data() -> dict[str, pd.DataFrame]:
    """Load expected raw CSV files."""
    raw_path = get_path("raw")
    frames: dict[str, pd.DataFrame] = {}
    missing = [filename for filename in RAW_FILES.values() if not (raw_path / filename).exists()]
    if missing:
        raise FileNotFoundError(f"Missing raw files: {missing}")
    for table, filename in RAW_FILES.items():
        frames[table] = pd.read_csv(raw_path / filename, keep_default_na=False)
    LOGGER.info("raw data loaded", extra={"tables": len(frames)})
    return frames
