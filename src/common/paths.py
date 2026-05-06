from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ensure_directory(path: Path) -> Path:
    """Create and return a directory."""
    path.mkdir(parents=True, exist_ok=True)
    return path
