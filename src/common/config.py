from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from src.common.paths import ROOT


@lru_cache
def get_settings() -> dict:
    """Load project settings."""
    with (ROOT / "config" / "settings.yaml").open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_path(name: str) -> Path:
    """Resolve a configured project path."""
    return ROOT / get_settings()["paths"][name]


def load_yaml(path: str | Path) -> dict:
    """Load a YAML file."""
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
