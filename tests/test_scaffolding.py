"""Smoke tests for the initial project scaffolding."""

import importlib


def test_package_imports() -> None:
    """Ensure the core package is discoverable after installation."""

    module = importlib.import_module("wordimperfect")
    assert module.__version__ == "0.1.0"


