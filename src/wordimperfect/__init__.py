"""Core package for the WordImperfect project.

This module currently exposes metadata used by packaging tooling. As the
application matures, shared functionality and public APIs will be surfaced here.
"""

__all__ = ["__version__", "Application"]

__version__ = "0.1.0"


def __getattr__(name: str):
    if name == "Application":
        from .app import Application

        return Application
    msg = f"module 'wordimperfect' has no attribute '{name}'"
    raise AttributeError(msg)

