"""Tests covering pure controller logic."""

from __future__ import annotations

from wordimperfect.controllers import (
    Alignment,
    EditingController,
    FormattingController,
    FormattingState,
    ListType,
    ObjectInsertionController,
    TextStyler,
)


def test_editing_controller_summary_counts() -> None:
    controller = EditingController()
    summary = controller.summarize("Hello world\nNext line")
    assert summary.characters == len("Hello world\nNext line")
    assert summary.words == 4
    assert summary.lines == 2


def test_formatting_controller_toggle_sequence() -> None:
    controller = FormattingController()
    assert controller.state == FormattingState()

    assert controller.toggle_bold() is True
    assert controller.toggle_italic() is True
    assert controller.toggle_underline() is True

    state = controller.state
    assert state.bold is True
    assert state.italic is True
    assert state.underline is True

    controller.reset()
    reset_state = controller.state
    assert reset_state.bold is False
    assert reset_state.italic is False
    assert reset_state.underline is False


def test_formatting_controller_font_and_colour() -> None:
    controller = FormattingController()
    controller.set_font_family("Courier New")
    controller.set_font_size(18)
    controller.set_foreground("#123456")
    state = controller.state
    assert state.font_family == "Courier New"
    assert state.font_size == 18
    assert state.foreground == "#123456"


def test_formatting_controller_paragraph_controls() -> None:
    controller = FormattingController()
    controller.set_alignment(Alignment.CENTER)
    controller.increase_indent()
    controller.increase_indent()
    controller.decrease_indent()
    state = controller.state
    assert state.alignment is Alignment.CENTER
    assert state.indent == 1
    controller.set_list_type(ListType.BULLET)
    assert controller.state.list_type is ListType.BULLET
    controller.clear_list_type()
    assert controller.state.list_type is ListType.NONE


def test_editing_controller_find_and_replace() -> None:
    controller = EditingController()
    text = "One fish two Fish red fish blue fish"
    matches = controller.find_occurrences(text, "fish", case_sensitive=False)
    assert matches == [4, 13, 22, 32]
    summary = controller.replace(text, "fish", "cat", replace_all=False)
    assert summary.replacements == 1
    assert summary.text.startswith("One cat")


def test_object_insertion_controller_executes_registered_handler() -> None:
    controller = ObjectInsertionController()
    executed: list[str] = []

    def handler() -> str:
        executed.append("called")
        return "result"

    controller.register_handler("Sample", handler)
    assert tuple(controller.available_objects()) == ("Sample",)
    outcome = controller.insert("Sample")
    assert outcome == "result"
    assert executed == ["called"]


class FakeTextWidget:
    def __init__(self, text: str) -> None:
        self.text = text
        self.cursor = 0
        self.selection: tuple[int, int] | None = None
        self.tag_configs: dict[str, dict[str, object]] = {}
        self.tag_ranges_called: list[tuple[str, str]] = []
        self.tag_add_calls: list[tuple[str, str, str]] = []
        self.tag_remove_calls: list[tuple[str, str, str]] = []
        self.widget_config: dict[str, object] = {}

    def set_selection(self, start: int, end: int) -> None:
        self.selection = (start, end)
        self.cursor = end

    def tag_configure(self, tag: str, **kwargs: object) -> None:
        self.tag_configs[tag] = kwargs

    def tag_add(self, tag: str, start: str, end: str) -> None:
        self.tag_add_calls.append((tag, start, end))

    def tag_remove(self, tag: str, start: str, end: str) -> None:
        self.tag_remove_calls.append((tag, start, end))

    def tag_ranges(self, tag: str):
        if tag != "sel" or self.selection is None:
            return ()
        start, end = self.selection
        return (self._offset_to_index(start), self._offset_to_index(end))

    def configure(self, **kwargs: object) -> None:
        self.widget_config.update(kwargs)

    def get(self, start: str, end: str) -> str:
        start_offset = self._index_to_offset(start)
        end_offset = self._index_to_offset(end)
        return self.text[start_offset:end_offset]

    def delete(self, start: str, end: str) -> None:
        start_offset = self._index_to_offset(start)
        end_offset = self._index_to_offset(end)
        self.text = self.text[:start_offset] + self.text[end_offset:]
        self.cursor = start_offset

    def insert(self, index: str, value: str) -> None:
        offset = self._index_to_offset(index)
        self.text = self.text[:offset] + value + self.text[offset:]
        self.cursor = offset + len(value)

    def index(self, spec: str) -> str:
        if spec == "insert":
            return self._offset_to_index(self.cursor)
        if spec == "insert linestart":
            line_start = self.text.rfind("\n", 0, self.cursor) + 1
            return self._offset_to_index(line_start)
        if spec == "insert lineend":
            line_end = self.text.find("\n", self.cursor)
            if line_end == -1:
                line_end = len(self.text)
            return self._offset_to_index(line_end)
        if spec == "end":
            return self._offset_to_index(len(self.text))
        return spec

    def _offset_to_index(self, offset: int) -> str:
        line = self.text.count("\n", 0, offset) + 1
        column = offset - (self.text.rfind("\n", 0, offset) + 1)
        return f"{line}.{column}"

    def _index_to_offset(self, index: str) -> int:
        if index == "end":
            return len(self.text)
        line_str, column_str = index.split(".")
        line = int(line_str)
        column = int(column_str)
        lines = self.text.splitlines(keepends=True)
        offset = sum(len(lines[i]) for i in range(min(line - 1, len(lines))))
        return offset + column


def test_text_styler_applies_inline_paragraph_and_list_formatting() -> None:
    fake = FakeTextWidget("alpha\nbeta")
    fake.set_selection(0, len(fake.text))
    styler = TextStyler(fake)
    controller = FormattingController()
    controller.toggle_bold()
    controller.set_font_family("Courier New")
    controller.set_font_size(14)
    controller.set_foreground("#0f0f0f")
    controller.set_alignment(Alignment.RIGHT)
    controller.increase_indent()
    controller.set_list_type(ListType.BULLET)

    styler.apply(controller.state)

    inline_cfg = fake.tag_configs[TextStyler.INLINE_TAG]
    assert inline_cfg["font"][0] == "Courier New"
    assert inline_cfg["font"][1] == 14
    assert inline_cfg["foreground"] == "#0f0f0f"
    assert fake.text.startswith("    \u2022 alpha")

