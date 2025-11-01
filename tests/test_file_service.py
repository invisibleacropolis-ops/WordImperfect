"""Tests for the :mod:`wordimperfect.services.file_service` module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wordimperfect.services import FileService


@pytest.fixture()
def service() -> FileService:
    return FileService()


def test_write_and_read_plain_text(tmp_path: Path, service: FileService) -> None:
    destination = tmp_path / "sample.txt"
    content = "Hello\nWorld"

    service.write(destination, content)
    assert destination.read_text(encoding="utf-8") == content
    assert service.read(destination) == content


def test_write_and_read_rtf(tmp_path: Path, service: FileService) -> None:
    destination = tmp_path / "sample.rtf"
    content = "Line 1\nLine 2\tTabbed"

    service.write(destination, content)
    text = service.read(destination)
    assert "Line 1" in destination.read_text(encoding="utf-8")  # encoded markup
    assert text == content


def test_write_and_read_docx(tmp_path: Path, service: FileService) -> None:
    pytest.importorskip("docx", reason="python-docx optional dependency not installed")
    destination = tmp_path / "sample.docx"
    content = "First line\nSecond line"

    service.write(destination, content)
    assert destination.exists()
    assert service.read(destination) == content


def test_read_unknown_extension_raises(tmp_path: Path, service: FileService) -> None:
    target = tmp_path / "unsupported.xyz"
    target.write_text("data", encoding="utf-8")

    with pytest.raises(ValueError):
        service.read(target)


def test_write_unknown_extension_raises(tmp_path: Path, service: FileService) -> None:
    target = tmp_path / "unsupported.xyz"

    with pytest.raises(ValueError):
        service.write(target, "text")


def test_read_with_styles_returns_metadata(tmp_path: Path, service: FileService) -> None:
    destination = tmp_path / "with_styles.txt"
    destination.write_text("payload", encoding="utf-8")
    metadata_path = destination.with_suffix(destination.suffix + ".styles.json")
    metadata_path.write_text(
        json.dumps({"0": {"alignment": "left", "indent": 2, "list_type": "bullet"}}),
        encoding="utf-8",
    )

    text, metadata = service.read_with_styles(destination)
    assert text == "payload"
    assert metadata == {0: {"alignment": "left", "indent": 2, "list_type": "bullet"}}


def test_write_with_styles_manages_sidecar(tmp_path: Path, service: FileService) -> None:
    destination = tmp_path / "styled.txt"
    payload = {0: {"alignment": "center", "indent": 1, "list_type": "numbered"}}

    service.write_with_styles(destination, "text", payload)
    assert destination.read_text(encoding="utf-8") == "text"

    metadata_path = destination.with_suffix(destination.suffix + ".styles.json")
    stored = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert stored == {
        "0": {"alignment": "center", "indent": 1, "list_type": "numbered"}
    }

    service.write_with_styles(destination, "text", {})
    assert metadata_path.exists() is False
