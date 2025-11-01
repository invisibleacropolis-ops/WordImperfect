"""Controller layer for the WordImperfect desktop application.

The controller modules expose small, testable units that orchestrate the
interaction between the GUI widgets and the pure services. Importing from this
package keeps the Tkinter driven interface thin while allowing the core logic to
be exercised independently.
"""

from .document_controller import DocumentController
from .editing_controller import EditingController, EditingSummary
from .formatting_controller import FormattingController, FormattingState

__all__ = [
    "DocumentController",
    "EditingController",
    "EditingSummary",
    "FormattingController",
    "FormattingState",
]

