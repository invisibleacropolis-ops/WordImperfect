"""Unit tests for :mod:`wordimperfect.controllers.document_controller`."""

from __future__ import annotations

from pathlib import Path

import pytest

from wordimperfect.controllers import DocumentController
from wordimperfect.services import FileService


@pytest.fixture()
def controller(tmp_path: Path) -> DocumentController:
    service = FileService()
    return DocumentController(service)


def test_new_document_resets_metadata(controller: DocumentController) -> None:
    controller.new_document()
    metadata = controller.metadata
    assert metadata.path is None
    assert metadata.is_modified is False


def test_save_without_path_raises(controller: DocumentController) -> None:
    with pytest.raises(ValueError):
        controller.save_document("text")


def test_open_and_save_round_trip(tmp_path: Path, controller: DocumentController) -> None:
    path = tmp_path / "example.txt"
    path.write_text("initial", encoding="utf-8")

    content = controller.open_document(path)
    assert content == "initial"
    assert controller.document_title() == "example.txt"

    controller.mark_modified()
    assert controller.metadata.is_modified is True

    controller.save_document("changed")
    assert path.read_text(encoding="utf-8") == "changed"
    assert controller.metadata.is_modified is False


def test_supported_filetypes_contains_expected_extensions(controller: DocumentController) -> None:
    entries = list(controller.supported_filetypes())
    patterns = {pattern for _, pattern in entries}
    assert {"*.rtf", "*.txt", "*.docx"}.issubset(patterns)

