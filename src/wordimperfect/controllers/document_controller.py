"""Document lifecycle management for the WordImperfect editor.

The :class:`DocumentController` centralises the logic required to create, load
and persist user authored documents. The controller intentionally does not
depend on Tkinter so it can be exercised through unit tests without the need for
GUI primitives.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from wordimperfect.controllers.formatting_controller import (
    Alignment,
    ListType,
    ParagraphStyleSnapshot,
)
from wordimperfect.services import FileService


@dataclass
class DocumentMetadata:
    """In-memory representation of the state of the current document."""

    path: Path | None = None
    is_modified: bool = False
    paragraph_styles: dict[int, ParagraphStyleSnapshot] = field(default_factory=dict)


class DocumentController:
    """Coordinate file operations for the active document.

    Parameters
    ----------
    file_service:
        Service responsible for the physical IO of files. The controller only
        describes *what* action should be performed; the service handles the
        implementation details for each supported format.
    """

    _SUPPORTED_FORMATS: tuple[tuple[str, str], ...] = (
        ("Rich Text Format", "*.rtf"),
        ("Plain Text", "*.txt"),
        ("Word Document", "*.docx"),
    )

    def __init__(self, file_service: FileService) -> None:
        self._file_service = file_service
        self._metadata = DocumentMetadata()

    # ------------------------------------------------------------------
    # Document state helpers
    # ------------------------------------------------------------------
    @property
    def metadata(self) -> DocumentMetadata:
        """Return a copy of the current document metadata."""

        return DocumentMetadata(
            path=self._metadata.path,
            is_modified=self._metadata.is_modified,
            paragraph_styles={
                index: ParagraphStyleSnapshot(
                    alignment=style.alignment,
                    indent=style.indent,
                    list_type=style.list_type,
                )
                for index, style in self._metadata.paragraph_styles.items()
            },
        )

    def mark_modified(self) -> None:
        """Flag the document as containing unsaved changes."""

        self._metadata.is_modified = True

    def mark_clean(self) -> None:
        """Flag the document as synchronised with its persisted contents."""

        self._metadata.is_modified = False

    # ------------------------------------------------------------------
    # Lifecycle actions
    # ------------------------------------------------------------------
    def new_document(self) -> None:
        """Reset the controller to track a brand-new, unsaved document."""

        self._metadata = DocumentMetadata()

    def clear_paragraph_styles(self) -> None:
        """Remove any tracked paragraph styling metadata."""

        self._metadata.paragraph_styles.clear()

    def open_document(self, path: Path) -> str:
        """Load a document from ``path`` and update the metadata.

        Parameters
        ----------
        path:
            File to load. The :class:`FileService` determines the exact parsing
            routine based on the file extension.

        Returns
        -------
        str
            The textual representation of the loaded document.
        """

        text, paragraph_styles = self._file_service.read_with_styles(path)
        metadata = DocumentMetadata(path=path, is_modified=False)
        for index, payload in paragraph_styles.items():
            if not isinstance(payload, dict):
                continue
            alignment_value = payload.get("alignment")
            indent_value = payload.get("indent")
            list_type_value = payload.get("list_type")

            alignment = self._coerce_alignment(alignment_value)
            list_type = self._coerce_list_type(list_type_value)
            indent_int = self._coerce_indent(indent_value)
            metadata.paragraph_styles[index] = ParagraphStyleSnapshot(
                alignment=alignment,
                indent=indent_int,
                list_type=list_type,
            )
        self._metadata = metadata
        return text

    def save_document(self, text: str, path: Path | None = None) -> Path:
        """Persist ``text`` either to ``path`` or the tracked file.

        Parameters
        ----------
        text:
            Content that should be written.
        path:
            Optional explicit destination. When omitted the controller falls
            back to the current document path and raises :class:`ValueError`
            when no such path exists.
        """

        destination = path or self._metadata.path
        if destination is None:
            msg = "Cannot save a document without a target path."
            raise ValueError(msg)

        paragraph_styles = self.export_paragraph_styles()
        payload = {
            index: {
                "alignment": style.alignment.value,
                "indent": style.indent,
                "list_type": style.list_type.value,
            }
            for index, style in paragraph_styles.items()
        }

        self._file_service.write_with_styles(destination, text, payload)
        self._metadata.path = destination
        self.mark_clean()
        return destination

    # ------------------------------------------------------------------
    # Metadata coercion helpers
    # ------------------------------------------------------------------
    def _coerce_alignment(self, value: object) -> Alignment:
        """Best-effort conversion of serialised alignment data."""

        if isinstance(value, Alignment):
            return value
        if isinstance(value, str):
            try:
                return Alignment(value)
            except ValueError:
                return Alignment.LEFT
        return Alignment.LEFT

    def _coerce_list_type(self, value: object) -> ListType:
        """Best-effort conversion of serialised list type data."""

        if isinstance(value, ListType):
            return value
        if isinstance(value, str):
            try:
                return ListType(value)
            except ValueError:
                return ListType.NONE
        return ListType.NONE

    def _coerce_indent(self, value: object) -> int:
        """Return a valid indent value derived from ``value``."""

        if isinstance(value, int):
            return max(0, value)
        if isinstance(value, str) and value.strip():
            try:
                return max(0, int(value))
            except ValueError:
                return 0
        return 0

    # ------------------------------------------------------------------
    # Styling metadata
    # ------------------------------------------------------------------
    def record_paragraph_style(
        self, paragraph_index: int, style: ParagraphStyleSnapshot
    ) -> None:
        """Persist the style assigned to ``paragraph_index`` in memory."""

        if paragraph_index < 0:
            msg = "Paragraph index must be non-negative"
            raise ValueError(msg)
        self._metadata.paragraph_styles[paragraph_index] = ParagraphStyleSnapshot(
            alignment=style.alignment,
            indent=style.indent,
            list_type=style.list_type,
        )

    def paragraph_style(self, paragraph_index: int) -> ParagraphStyleSnapshot | None:
        """Return the stored style for ``paragraph_index`` if one exists."""

        style = self._metadata.paragraph_styles.get(paragraph_index)
        if style is None:
            return None
        return ParagraphStyleSnapshot(
            alignment=style.alignment,
            indent=style.indent,
            list_type=style.list_type,
        )

    def export_paragraph_styles(self) -> dict[int, ParagraphStyleSnapshot]:
        """Return a shallow copy of the tracked paragraph styling metadata."""

        return {
            index: ParagraphStyleSnapshot(
                alignment=style.alignment,
                indent=style.indent,
                list_type=style.list_type,
            )
            for index, style in self._metadata.paragraph_styles.items()
        }

    # ------------------------------------------------------------------
    # User interface helpers
    # ------------------------------------------------------------------
    def document_title(self) -> str:
        """Return a human friendly document name for window titles."""

        return self._metadata.path.name if self._metadata.path else "Untitled"

    def supported_filetypes(self) -> Iterable[tuple[str, str]]:
        """Expose the file type filter definitions for file dialogs."""

        return self._SUPPORTED_FORMATS
