"""Utilities that perform pure text editing computations.

The :class:`EditingController` is intentionally detached from Tkinter widgets so
the same logic can be used inside the GUI and under test. The controller
provides basic statistics today and can be evolved with more operations without
entangling presentation concerns.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EditingSummary:
    """Aggregated metrics describing the current editing session."""

    characters: int
    words: int
    lines: int


class EditingController:
    """Compute derived information from textual content."""

    def summarize(self, text: str) -> EditingSummary:
        """Return length, word and line statistics for ``text``.

        Parameters
        ----------
        text:
            Arbitrary unicode text entered by the user.
        """

        characters = len(text)
        normalized = text.strip()
        words = len(normalized.split()) if normalized else 0
        lines = text.count("\n") + 1 if text else 0
        return EditingSummary(characters=characters, words=words, lines=lines)

