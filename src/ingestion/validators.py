from __future__ import annotations

import pandas as pd

from src.common.config import load_yaml
from src.common.paths import ROOT


def validate_required_columns(frames: dict[str, pd.DataFrame]) -> None:
    """Validate raw input schemas."""
    rules = load_yaml(ROOT / "config" / "data_quality_rules.yaml")
    for table, config in rules.items():
        required = set(config.get("required_columns", []))
        missing = sorted(required - set(frames[table].columns))
        if missing:
            raise ValueError(f"{table} missing required columns: {missing}")
