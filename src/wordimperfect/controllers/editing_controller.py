"""Utilities that perform pure text editing computations.

The :class:`EditingController` is intentionally detached from Tkinter widgets so
the same logic can be used inside the GUI and under test. The controller
provides basic statistics today and can be evolved with more operations without
entangling presentation concerns.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EditingSummary:
    """Aggregated metrics describing the current editing session."""

    characters: int
    words: int
    lines: int


@dataclass(frozen=True, slots=True)
class SearchMatches:
    """Container describing all matches for a given query."""

    query: str
    positions: tuple[int, ...]

    def spans(self) -> tuple[tuple[int, int], ...]:
        """Return inclusive-exclusive spans suitable for highlighting."""

        length = len(self.query)
        return tuple((start, start + length) for start in self.positions)


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

    # ------------------------------------------------------------------
    # Search helpers
    # ------------------------------------------------------------------
    def find_matches(
        self, text: str, query: str, *, case_sensitive: bool = False
    ) -> SearchMatches:
        """Return all match offsets for ``query`` within ``text``.

        Parameters
        ----------
        text:
            The text that should be searched.
        query:
            Substring that should be located.
        case_sensitive:
            Whether to perform a case sensitive comparison.
        """

        if not query:
            return SearchMatches(query=query, positions=())
        haystack = text if case_sensitive else text.lower()
        needle = query if case_sensitive else query.lower()
        matches: list[int] = []
        index = haystack.find(needle)
        while index != -1:
            matches.append(index)
            index = haystack.find(needle, index + len(needle) or index + 1)
        return SearchMatches(query=query, positions=tuple(matches))

    def find_occurrences(
        self, text: str, query: str, *, case_sensitive: bool = False
    ) -> list[int]:
        """Backward-compatible wrapper around :meth:`find_matches`."""

        return list(
            self.find_matches(text, query, case_sensitive=case_sensitive).positions
        )

    def next_occurrence(
        self,
        text: str,
        query: str,
        *,
        start: int = 0,
        case_sensitive: bool = False,
        wrap: bool = False,
    ) -> int | None:
        """Return the index of the next occurrence at or after ``start``.

        When ``wrap`` is ``True`` the search will restart from the beginning if
        no further matches are found beyond ``start``. ``None`` is returned when
        no match exists.
        """

        matches = self.find_matches(text, query, case_sensitive=case_sensitive)
        for position in matches.positions:
            if position >= start:
                return position
        if wrap and matches.positions:
            return matches.positions[0]
        return None

    def replace(
        self,
        text: str,
        query: str,
        replacement: str,
        *,
        case_sensitive: bool = False,
        replace_all: bool = True,
    ) -> ReplacementSummary:
        """Replace occurrences of ``query`` with ``replacement``.

        Returns a :class:`ReplacementSummary` detailing how many substitutions
        were performed and the resulting text. When ``replace_all`` is ``False``
        only the first match is replaced.
        """

        if not query:
            return ReplacementSummary(text=text, replacements=0, positions=[])
        matches = self.find_matches(text, query, case_sensitive=case_sensitive)
        if not matches.positions:
            return ReplacementSummary(text=text, replacements=0, positions=[])

        if not replace_all:
            first = matches.positions[0]
            new_text = text[:first] + replacement + text[first + len(query) :]
            return ReplacementSummary(text=new_text, replacements=1, positions=[first])

        segments: list[str] = []
        last_index = 0
        for match in matches.positions:
            segments.append(text[last_index:match])
            segments.append(replacement)
            last_index = match + len(query)
        segments.append(text[last_index:])
        new_text = "".join(segments)
        return ReplacementSummary(
            text=new_text, replacements=len(matches.positions), positions=matches.positions
        )


@dataclass(frozen=True, slots=True)
class ReplacementSummary:
    """Detailed information about a find & replace operation."""

    text: str
    replacements: int
    positions: Iterable[int]
