from __future__ import annotations

import json

import duckdb
import pandas as pd

from src.common.config import get_path
from src.common.paths import ensure_directory


def write_feature_store(features: pd.DataFrame) -> None:
    """Persist features to CSV, DuckDB, metadata, and quality scorecards."""
    output = ensure_directory(get_path("features"))
    scorecards = ensure_directory(get_path("scorecards"))
    db_path = output / "fraud_feature_store.duckdb"
    features.to_csv(output / "transaction_features.csv", index=False)
    with duckdb.connect(str(db_path)) as connection:
        connection.execute("CREATE OR REPLACE TABLE transaction_features AS SELECT * FROM features")
    metadata = {
        "feature_count": int(len([c for c in features.columns if c not in {"transaction_id"}])),
        "row_count": int(len(features)),
        "feature_store_path": str(db_path),
    }
    (output / "feature_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    report = pd.DataFrame(
        [
            {
                "feature_name": col,
                "missing_rate": float(features[col].isna().mean()),
                "dtype": str(features[col].dtype),
            }
            for col in features.columns
        ]
    )
    summary = {
        "row_count": int(len(features)),
        "feature_count": int(len(features.columns)),
        "max_missing_rate": float(report["missing_rate"].max()),
    }
    report.to_csv(scorecards / "feature_store_quality_report.csv", index=False)
    (scorecards / "feature_store_quality_report.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
