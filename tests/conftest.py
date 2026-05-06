from __future__ import annotations

import pytest

from src.pipeline.run_all import run_pipeline


@pytest.fixture(scope="session")
def pipeline_outputs() -> None:
    run_pipeline()
