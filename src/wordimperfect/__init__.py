"""Core package for the WordImperfect project.

This module currently exposes metadata used by packaging tooling. As the
application matures, shared functionality and public APIs will be surfaced here.
"""

from .app import Application

__all__ = ["__version__", "Application"]

__version__ = "0.1.0"

