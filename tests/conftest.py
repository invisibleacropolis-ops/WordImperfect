"""Test configuration for the WordImperfect project."""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    """Ensure the `src` directory is importable during local test runs."""

    root = Path(__file__).resolve().parent.parent
    src_path = root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
