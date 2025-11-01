"""File IO routines for the WordImperfect editor."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Final

try:
    from docx import Document
except ImportError:  # pragma: no cover - optional dependency
    Document = None  # type: ignore[assignment]


class FileService:
    """Read and write documents in the supported formats."""

    _ENCODING: Final = "utf-8"
    _DOCX_SUFFIX: Final = ".docx"
    _RTF_SUFFIX: Final = ".rtf"
    _TEXT_SUFFIX: Final = ".txt"

    def read(self, path: Path) -> str:
        """Return the textual contents of ``path``.

        The method inspects the file extension to determine the appropriate
        decoding routine. The implementation is intentionally lightweight so the
        editor can start life without external services.
        """

        suffix = path.suffix.lower()
        if suffix == self._TEXT_SUFFIX:
            return path.read_text(encoding=self._ENCODING)
        if suffix == self._RTF_SUFFIX:
            return self._decode_rtf(path.read_text(encoding=self._ENCODING))
        if suffix == self._DOCX_SUFFIX:
            if Document is None:
                msg = "python-docx is required to read .docx files"
                raise RuntimeError(msg)
            document = Document(path)
            return "\n".join(paragraph.text for paragraph in document.paragraphs)

        msg = f"Unsupported file format: {path.suffix}"
        raise ValueError(msg)

    def write(self, path: Path, text: str) -> None:
        """Persist ``text`` to ``path`` using the format implied by the suffix."""

        suffix = path.suffix.lower()
        if suffix == self._TEXT_SUFFIX:
            path.write_text(text, encoding=self._ENCODING)
            return
        if suffix == self._RTF_SUFFIX:
            path.write_text(self._encode_rtf(text), encoding=self._ENCODING)
            return
        if suffix == self._DOCX_SUFFIX:
            if Document is None:
                msg = "python-docx is required to write .docx files"
                raise RuntimeError(msg)
            document = Document()
            lines = text.splitlines()
            if text.endswith("\n"):
                lines.append("")
            if not lines:
                lines = [""]
            for line in lines:
                document.add_paragraph(line)
            document.save(path)
            return

        msg = f"Unsupported file format: {path.suffix}"
        raise ValueError(msg)

    # ------------------------------------------------------------------
    # RTF helpers
    # ------------------------------------------------------------------
    def _encode_rtf(self, text: str) -> str:
        """Return a compact Rich Text Format representation of ``text``."""

        escaped = (
            text.replace("\\", r"\\")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("\t", r"\tab ")
        )
        escaped = escaped.replace("\r\n", "\n")
        escaped = escaped.replace("\n", "\\par\n")
        buffer = io.StringIO()
        buffer.write("{\\rtf1\\ansi\n")
        buffer.write(escaped)
        buffer.write("\n}")
        return buffer.getvalue()

    def _decode_rtf(self, rtf: str) -> str:
        """Best-effort conversion of a subset of RTF into plain text."""

        result: list[str] = []
        i = 0
        length = len(rtf)
        while i < length:
            char = rtf[i]
            if char == "\\":
                i += 1
                if i >= length:
                    break
                next_char = rtf[i]
                if next_char in "\\{}":
                    result.append(next_char)
                    i += 1
                    continue

                control_start = i
                while i < length and rtf[i].isalpha():
                    i += 1
                control_word = rtf[control_start:i]

                sign = 1
                if i < length and rtf[i] == "-":
                    sign = -1
                    i += 1
                number_start = i
                while i < length and rtf[i].isdigit():
                    i += 1
                if number_start != i:
                    _ = int(rtf[number_start:i]) * sign

                if i < length and rtf[i] == " ":
                    i += 1

                if control_word in {"par", "line"}:
                    result.append("\n")
                elif control_word == "tab":
                    result.append("\t")
                continue

            if char in "{}":
                i += 1
                continue

            if char in "\r\n":
                i += 1
                continue

            result.append(char)
            i += 1

        return "".join(result)
