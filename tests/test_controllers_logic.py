"""Tests covering pure controller logic."""

from __future__ import annotations

from wordimperfect.controllers import (
    EditingController,
    FormattingController,
    FormattingState,
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

