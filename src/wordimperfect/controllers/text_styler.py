"""Helpers that translate formatting state into Tkinter text widget mutations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, cast

from .formatting_controller import Alignment, FormattingState, ListType


class TextWidget(Protocol):
    def tag_configure(self, tag: str, *args: object, **kwargs: object) -> object: ...

    def tag_add(self, tag: str, *args: str) -> None: ...

    def tag_remove(self, tag: str, *args: str) -> None: ...

    def configure(self, *args: object, **kwargs: object) -> object: ...

    def get(self, start: str, end: str) -> str: ...

    def delete(self, start: str, end: str) -> None: ...

    def insert(self, index: str, value: str) -> None: ...

    def tag_ranges(self, tag: str) -> Iterable[str]: ...

    def index(self, index: str) -> str: ...


@dataclass
class _IndexRange:
    start: str
    end: str


class TextStyler:
    """Apply :class:`FormattingState` information to a Tk text widget."""

    INLINE_TAG = "wi_inline"
    ALIGN_TAG_PREFIX = "wi_align_"
    INDENT_WIDTH = 20

    def __init__(self, widget: object) -> None:
        self._widget = cast(TextWidget, widget)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def apply(self, state: FormattingState) -> None:
        """Apply inline, paragraph and list formatting in one operation."""

        self._apply_list(state)
        self._apply_inline(state)
        self._apply_paragraph(state)

    # ------------------------------------------------------------------
    # Inline formatting
    # ------------------------------------------------------------------
    def _apply_inline(self, state: FormattingState) -> None:
        weight = "bold" if state.bold else "normal"
        slant = "italic" if state.italic else "roman"
        decorations: list[str] = []
        if state.underline:
            decorations.append("underline")
        style = " ".join(
            filter(
                None,
                (
                    weight if weight != "normal" else "",
                    slant if slant != "roman" else "",
                    *decorations,
                ),
            )
        )
        if not style:
            style = "normal"
        font = (state.font_family, state.font_size, style)
        self._widget.tag_configure(
            self.INLINE_TAG, font=font, foreground=state.foreground
        )

        selection = self._selection_range()
        if selection:
            self._widget.tag_add(self.INLINE_TAG, selection.start, selection.end)
        else:
            self._widget.configure(font=font, foreground=state.foreground)

    # ------------------------------------------------------------------
    # Paragraph formatting
    # ------------------------------------------------------------------
    def _apply_paragraph(self, state: FormattingState) -> None:
        indent_px = state.indent * self.INDENT_WIDTH
        for alignment in Alignment:
            tag = self.ALIGN_TAG_PREFIX + alignment.value
            self._widget.tag_configure(
                tag, justify=alignment.value, lmargin1=indent_px, lmargin2=indent_px
            )

        selection = self._selection_range() or _IndexRange("1.0", "end")
        for alignment in Alignment:
            tag = self.ALIGN_TAG_PREFIX + alignment.value
            self._widget.tag_remove(tag, selection.start, selection.end)
        active_tag = self.ALIGN_TAG_PREFIX + state.alignment.value
        self._widget.tag_add(active_tag, selection.start, selection.end)

    # ------------------------------------------------------------------
    # List formatting
    # ------------------------------------------------------------------
    def _apply_list(self, state: FormattingState) -> None:
        if state.list_type is ListType.NONE:
            return
        selection = self._selection_range()
        if not selection:
            selection = self._line_range_at_insert()
        content = self._widget.get(selection.start, selection.end)
        if not content:
            return
        lines = content.splitlines()
        new_lines: list[str] = []
        for index, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            indent = " " * (state.indent * 4)
            if state.list_type is ListType.BULLET:
                prefix = "\u2022 "
            else:
                prefix = f"{index}. "
            new_lines.append(indent + prefix + stripped)
        replacement = "\n".join(new_lines)
        self._widget.delete(selection.start, selection.end)
        self._widget.insert(selection.start, replacement)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _selection_range(self) -> _IndexRange | None:
        ranges: Iterable[str] = self._widget.tag_ranges("sel")
        values = list(map(str, ranges))
        if len(values) >= 2:
            return _IndexRange(start=values[0], end=values[1])
        return None

    def _line_range_at_insert(self) -> _IndexRange:
        start = str(self._widget.index("insert linestart"))
        end = str(self._widget.index("insert lineend"))
        return _IndexRange(start=start, end=end)


__all__ = ["TextStyler"]
