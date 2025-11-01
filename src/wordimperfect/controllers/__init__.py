"""Controller layer for the WordImperfect desktop application.

The controller modules expose small, testable units that orchestrate the
interaction between the GUI widgets and the pure services. Importing from this
package keeps the Tkinter driven interface thin while allowing the core logic to
be exercised independently.
"""

from .document_controller import DocumentController
from .editing_controller import (
    EditingController,
    EditingSummary,
    ReplacementSummary,
    SearchMatches,
)
from .formatting_controller import (
    Alignment,
    FormattingController,
    FormattingState,
    ListType,
    ParagraphStyleSnapshot,
)
from .object_insertion_controller import ObjectInsertionController
from .text_styler import TextStyler

__all__ = [
    "DocumentController",
    "EditingController",
    "EditingSummary",
    "ReplacementSummary",
    "SearchMatches",
    "Alignment",
    "ListType",
    "FormattingController",
    "FormattingState",
    "ParagraphStyleSnapshot",
    "ObjectInsertionController",
    "TextStyler",
]
