"""Formatting state helpers for the WordImperfect editor.

The controller keeps track of the desired inline formatting toggles. The GUI is
responsible for binding these states to Tkinter text widget tags, but the
controller can be unit tested independently, ensuring that the application logic
remains deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FormattingState:
    """Flags that indicate whether certain inline styles are active."""

    bold: bool = False
    italic: bool = False
    underline: bool = False


class FormattingController:
    """Mutate :class:`FormattingState` instances based on user actions."""

    def __init__(self) -> None:
        self._state = FormattingState()

    @property
    def state(self) -> FormattingState:
        """Expose a copy of the current state for display purposes."""

        return FormattingState(
            bold=self._state.bold,
            italic=self._state.italic,
            underline=self._state.underline,
        )

    # ------------------------------------------------------------------
    # Toggling
    # ------------------------------------------------------------------
    def toggle_bold(self) -> bool:
        """Flip the bold toggle and return the resulting value."""

        self._state.bold = not self._state.bold
        return self._state.bold

    def toggle_italic(self) -> bool:
        """Flip the italic toggle and return the resulting value."""

        self._state.italic = not self._state.italic
        return self._state.italic

    def toggle_underline(self) -> bool:
        """Flip the underline toggle and return the resulting value."""

        self._state.underline = not self._state.underline
        return self._state.underline

    # ------------------------------------------------------------------
    # House keeping
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Clear all inline formatting toggles."""

        self._state = FormattingState()

