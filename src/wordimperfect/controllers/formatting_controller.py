"""Formatting state helpers for the WordImperfect editor.

The controller keeps track of the desired inline formatting toggles. The GUI is
responsible for binding these states to Tkinter text widget tags, but the
controller can be unit tested independently, ensuring that the application logic
remains deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Alignment(Enum):
    """Supported paragraph alignments."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class ListType(Enum):
    """Bullet and numbering list types."""

    NONE = "none"
    BULLET = "bullet"
    NUMBERED = "numbered"


@dataclass(slots=True)
class FormattingState:
    """Flags that indicate whether certain inline styles are active."""

    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_family: str = "Arial"
    font_size: int = 12
    foreground: str = "#000000"
    alignment: Alignment = Alignment.LEFT
    indent: int = 0
    list_type: ListType = ListType.NONE


@dataclass(slots=True)
class ParagraphStyleSnapshot:
    """Serialisable representation of paragraph level formatting."""

    alignment: Alignment
    indent: int
    list_type: ListType


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
            font_family=self._state.font_family,
            font_size=self._state.font_size,
            foreground=self._state.foreground,
            alignment=self._state.alignment,
            indent=self._state.indent,
            list_type=self._state.list_type,
        )

    def paragraph_style(self) -> ParagraphStyleSnapshot:
        """Return a snapshot of the current paragraph level formatting."""

        return ParagraphStyleSnapshot(
            alignment=self._state.alignment,
            indent=self._state.indent,
            list_type=self._state.list_type,
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

    # ------------------------------------------------------------------
    # Font management
    # ------------------------------------------------------------------
    def set_font_family(self, family: str) -> str:
        """Persist the preferred font family and return it."""

        if not family:
            return self._state.font_family
        self._state.font_family = family
        return family

    def set_font_size(self, size: int) -> int:
        """Persist the preferred font size ensuring it stays positive."""

        if size <= 0:
            return self._state.font_size
        self._state.font_size = size
        return size

    def set_foreground(self, color: str) -> str:
        """Persist the preferred foreground colour."""

        if not color:
            return self._state.foreground
        self._state.foreground = color
        return color

    # ------------------------------------------------------------------
    # Paragraph management
    # ------------------------------------------------------------------
    def set_alignment(self, alignment: Alignment | str) -> Alignment:
        """Update the paragraph alignment."""

        if isinstance(alignment, str):
            try:
                alignment = Alignment(alignment)
            except ValueError:
                return self._state.alignment
        self._state.alignment = alignment
        return alignment

    def cycle_alignment(self) -> Alignment:
        """Rotate through the alignment options left → centre → right."""

        order = (Alignment.LEFT, Alignment.CENTER, Alignment.RIGHT)
        index = order.index(self._state.alignment)
        alignment = order[(index + 1) % len(order)]
        self._state.alignment = alignment
        return alignment

    def increase_indent(self) -> int:
        """Increase the indent depth and return the new value."""

        self._state.indent += 1
        return self._state.indent

    def decrease_indent(self) -> int:
        """Decrease the indent depth without dropping below zero."""

        if self._state.indent > 0:
            self._state.indent -= 1
        return self._state.indent

    # ------------------------------------------------------------------
    # List support
    # ------------------------------------------------------------------
    def set_list_type(self, list_type: ListType | str) -> ListType:
        """Select the active list style."""

        if isinstance(list_type, str):
            try:
                list_type = ListType(list_type)
            except ValueError:
                return self._state.list_type
        self._state.list_type = list_type
        return list_type

    def clear_list_type(self) -> None:
        """Clear any active list styling."""

        self._state.list_type = ListType.NONE
