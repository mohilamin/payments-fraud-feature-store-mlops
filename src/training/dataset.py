from __future__ import annotations

import pandas as pd

from src.common.config import get_path, load_yaml
from src.common.paths import ROOT, ensure_directory


def load_feature_table() -> pd.DataFrame:
    """Load transaction features."""
    return pd.read_csv(get_path("features") / "transaction_features.csv")


def feature_columns() -> list[str]:
    """Return configured model feature columns."""
    return load_yaml(ROOT / "config" / "model_config.yaml")["feature_columns"]


def build_training_dataset(features: pd.DataFrame | None = None) -> pd.DataFrame:
    """Build and write the model training dataset."""
    features = features if features is not None else load_feature_table()
    cols = ["transaction_id", "transaction_timestamp", "fraud_label", *feature_columns()]
    dataset = features[cols].copy()
    ensure_directory(get_path("training"))
    dataset.to_csv(get_path("training") / "training_dataset.csv", index=False)
    return dataset
