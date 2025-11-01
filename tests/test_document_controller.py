"""Unit tests for :mod:`wordimperfect.controllers.document_controller`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wordimperfect.controllers import (
    Alignment,
    DocumentController,
    FormattingController,
    ListType,
)
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


def test_open_and_save_round_trip(
    tmp_path: Path, controller: DocumentController
) -> None:
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


def test_supported_filetypes_contains_expected_extensions(
    controller: DocumentController,
) -> None:
    entries = list(controller.supported_filetypes())
    patterns = {pattern for _, pattern in entries}
    assert {"*.rtf", "*.txt", "*.docx"}.issubset(patterns)


def test_paragraph_style_round_trip(controller: DocumentController) -> None:
    formatting = FormattingController()
    formatting.set_alignment(Alignment.RIGHT)
    formatting.increase_indent()

    controller.record_paragraph_style(0, formatting.paragraph_style())
    snapshot = controller.paragraph_style(0)
    assert snapshot is not None
    assert snapshot.alignment is Alignment.RIGHT
    assert snapshot.indent == 1

    styles = controller.export_paragraph_styles()
    assert 0 in styles


def test_paragraph_style_requires_non_negative_index(
    controller: DocumentController,
) -> None:
    formatting = FormattingController()
    with pytest.raises(ValueError):
        controller.record_paragraph_style(-1, formatting.paragraph_style())


def test_save_and_open_preserves_paragraph_styles(
    tmp_path: Path, controller: DocumentController
) -> None:
    destination = tmp_path / "styled.txt"
    formatting = FormattingController()
    formatting.set_alignment(Alignment.CENTER)
    formatting.increase_indent()
    formatting.set_list_type(ListType.BULLET)

    controller.record_paragraph_style(2, formatting.paragraph_style())
    controller.save_document("content", destination)

    metadata_path = destination.with_suffix(destination.suffix + ".styles.json")
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert payload == {
        "2": {
            "alignment": Alignment.CENTER.value,
            "indent": 1,
            "list_type": ListType.BULLET.value,
        }
    }

    controller.new_document()
    loaded_text = controller.open_document(destination)
    assert loaded_text == "content"

    restored = controller.paragraph_style(2)
    assert restored is not None
    assert restored.alignment is Alignment.CENTER
    assert restored.indent == 1
    assert restored.list_type is ListType.BULLET
