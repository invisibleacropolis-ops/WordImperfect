"""Document lifecycle management for the WordImperfect editor.

The :class:`DocumentController` centralises the logic required to create, load
and persist user authored documents. The controller intentionally does not
depend on Tkinter so it can be exercised through unit tests without the need for
GUI primitives.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from wordimperfect.services import FileService


@dataclass
class DocumentMetadata:
    """In-memory representation of the state of the current document."""

    path: Path | None = None
    is_modified: bool = False


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

        return DocumentMetadata(path=self._metadata.path, is_modified=self._metadata.is_modified)

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

        text = self._file_service.read(path)
        self._metadata = DocumentMetadata(path=path, is_modified=False)
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

        self._file_service.write(destination, text)
        self._metadata.path = destination
        self.mark_clean()
        return destination

    # ------------------------------------------------------------------
    # User interface helpers
    # ------------------------------------------------------------------
    def document_title(self) -> str:
        """Return a human friendly document name for window titles."""

        return self._metadata.path.name if self._metadata.path else "Untitled"

    def supported_filetypes(self) -> Iterable[tuple[str, str]]:
        """Expose the file type filter definitions for file dialogs."""

        return self._SUPPORTED_FORMATS

