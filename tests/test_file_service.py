"""Tests for the :mod:`wordimperfect.services.file_service` module."""

from __future__ import annotations

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

