"""Interactive Find & Replace dialog for the Tkinter front-end."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from wordimperfect.controllers import EditingController, SearchMatches


class FindReplaceDialog:
    """Modal dialog that performs incremental find & replace actions."""

    def __init__(
        self,
        master: tk.Misc,
        text_widget: tk.Text,
        editing_controller: EditingController,
        *,
        highlight_callback: Callable[[int, int], None],
        clear_highlight_callback: Callable[[], None],
        replace_callback: Callable[[int, int, str], None],
        replace_all_callback: Callable[[str], None],
        on_close: Callable[[], None],
    ) -> None:
        self._master = master
        self._text = text_widget
        self._editing_controller = editing_controller
        self._highlight_callback = highlight_callback
        self._clear_highlight_callback = clear_highlight_callback
        self._replace_callback = replace_callback
        self._replace_all_callback = replace_all_callback
        self._on_close = on_close

        self._matches: SearchMatches | None = None
        self._current_index: int = -1
        self._active_span: tuple[int, int] | None = None
        self._last_text: str = ""
        self._last_query: str = ""
        self._last_case_sensitive: bool = False

        self._find_var = tk.StringVar()
        self._replace_var = tk.StringVar()
        self._case_sensitive_var = tk.BooleanVar(value=False)
        self._status_var = tk.StringVar(value="Enter search text.")

        self._window = tk.Toplevel(master)
        self._window.title("Find & Replace")
        self._window.transient(master)
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", self.close)
        self._window.bind("<Escape>", lambda event: self.close())
        self._window.bind("<Return>", lambda event: self.find_next())
        self._window.bind("<Control-Return>", lambda event: self.replace_and_find())

        frame = ttk.Frame(self._window, padding=12)
        frame.grid(row=0, column=0, sticky=tk.NSEW)

        ttk.Label(frame, text="Find:").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))
        self._find_entry = ttk.Entry(frame, textvariable=self._find_var, width=32)
        self._find_entry.grid(row=0, column=1, sticky=tk.EW, pady=(0, 6))
        self._find_entry.focus_set()

        ttk.Label(frame, text="Replace:").grid(row=1, column=0, sticky=tk.W, pady=(0, 6))
        replace_entry = ttk.Entry(frame, textvariable=self._replace_var, width=32)
        replace_entry.grid(row=1, column=1, sticky=tk.EW, pady=(0, 6))

        button_column = ttk.Frame(frame)
        button_column.grid(row=0, column=2, rowspan=3, padx=(12, 0), sticky=tk.NS)

        find_next_btn = ttk.Button(button_column, text="Find Next", command=self.find_next)
        find_prev_btn = ttk.Button(
            button_column, text="Find Previous", command=self.find_previous
        )
        replace_btn = ttk.Button(button_column, text="Replace", command=self.replace_current)
        replace_find_btn = ttk.Button(
            button_column, text="Replace && Find", command=self.replace_and_find
        )
        replace_all_btn = ttk.Button(
            button_column, text="Replace All", command=self.replace_all
        )
        close_btn = ttk.Button(button_column, text="Close", command=self.close)

        for index, widget in enumerate(
            (
                find_next_btn,
                find_prev_btn,
                replace_btn,
                replace_find_btn,
                replace_all_btn,
                close_btn,
            )
        ):
            widget.grid(row=index, column=0, pady=2, sticky=tk.EW)

        case_checkbox = ttk.Checkbutton(
            frame,
            text="Case sensitive",
            variable=self._case_sensitive_var,
            command=self._reset_search,
        )
        case_checkbox.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        status = ttk.Label(frame, textvariable=self._status_var, anchor=tk.W)
        status.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(12, 0))

        frame.columnconfigure(1, weight=1)

        self._find_var.trace_add("write", self._reset_search)

        self._window.grab_set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def focus(self) -> None:
        """Return focus to the find text box."""

        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()
        self._find_entry.focus_set()

    def find_next(self) -> None:
        """Highlight the next occurrence, wrapping to the start as needed."""

        if not self._prepare_search():
            return
        assert self._matches is not None
        total = len(self._matches.positions)
        next_index = 0 if self._current_index == -1 else (self._current_index + 1) % total
        self._goto_match(next_index)

    def find_previous(self) -> None:
        """Highlight the previous occurrence, wrapping to the end as needed."""

        if not self._prepare_search():
            return
        assert self._matches is not None
        total = len(self._matches.positions)
        if self._current_index == -1:
            prev_index = total - 1
        else:
            prev_index = (self._current_index - 1) % total
        self._goto_match(prev_index)

    def replace_current(self) -> None:
        """Replace the currently highlighted match if one exists."""

        if not self._prepare_search():
            return
        if self._active_span is None:
            # No current match is highlighted; highlight the next match first.
            self.find_next()
            if self._active_span is None:
                return
        start, end = self._active_span
        replacement = self._replace_var.get()
        self._replace_callback(start, end, replacement)
        anchor = start + len(replacement)
        if not self._reset_after_edit(anchor):
            self._highlight_callback(start, anchor)
            self._status_var.set("Replaced 1 occurrence. No matches remain.")
            return
        self._highlight_callback(start, anchor)
        self._status_var.set("Replaced 1 occurrence.")

    def replace_and_find(self) -> None:
        """Replace the current match and immediately highlight the next one."""

        self.replace_current()
        if self._matches is None or not self._matches.positions:
            return
        self.find_next()

    def replace_all(self) -> None:
        """Replace all occurrences of the query within the text widget."""

        query = self._find_var.get()
        if not query:
            self._status_var.set("Enter search text before replacing.")
            return
        text = self._text.get("1.0", "end-1c")
        summary = self._editing_controller.replace(
            text,
            query,
            self._replace_var.get(),
            case_sensitive=self._case_sensitive_var.get(),
            replace_all=True,
        )
        if summary.replacements == 0:
            messagebox.showinfo("Find & Replace", "No matches were found to replace.")
            self._status_var.set("No matches were replaced.")
            return
        self._replace_all_callback(summary.text)
        self._clear_highlight_callback()
        self._matches = None
        self._current_index = -1
        self._active_span = None
        self._last_text = summary.text
        self._status_var.set(
            f"Replaced {summary.replacements} occurrence(s)."
        )
        messagebox.showinfo(
            "Find & Replace", f"Replaced {summary.replacements} occurrence(s)."
        )

    def close(self) -> None:
        """Close the dialog and clear any active highlights."""

        self._clear_highlight_callback()
        self._window.grab_release()
        self._window.destroy()
        self._on_close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _prepare_search(self) -> bool:
        query = self._find_var.get()
        if not query:
            self._status_var.set("Enter search text.")
            self._clear_highlight_callback()
            self._matches = None
            self._current_index = -1
            self._active_span = None
            return False

        text = self._text.get("1.0", "end-1c")
        case_sensitive = self._case_sensitive_var.get()
        matches = self._editing_controller.find_matches(
            text, query, case_sensitive=case_sensitive
        )
        if matches.positions:
            if (
                query != self._last_query
                or case_sensitive != self._last_case_sensitive
                or text != self._last_text
            ):
                self._current_index = -1
            self._matches = matches
            self._last_query = query
            self._last_case_sensitive = case_sensitive
            self._last_text = text
            return True

        self._matches = matches
        self._current_index = -1
        self._active_span = None
        self._clear_highlight_callback()
        self._status_var.set("No matches found.")
        return False

    def _goto_match(self, index: int) -> None:
        assert self._matches is not None
        total = len(self._matches.positions)
        index %= total
        self._current_index = index
        start = self._matches.positions[index]
        end = start + len(self._matches.query)
        self._active_span = (start, end)
        self._highlight_callback(start, end)
        self._status_var.set(f"Match {index + 1} of {total}.")

    def _reset_after_edit(self, anchor: int) -> bool:
        text = self._text.get("1.0", "end-1c")
        matches = self._editing_controller.find_matches(
            text,
            self._find_var.get(),
            case_sensitive=self._case_sensitive_var.get(),
        )
        self._matches = matches if matches.positions else None
        self._last_text = text
        if self._matches is None:
            self._current_index = -1
            self._active_span = None
            self._clear_highlight_callback()
            return False
        positions = self._matches.positions
        next_index = next((i for i, pos in enumerate(positions) if pos >= anchor), 0)
        self._current_index = (next_index - 1) % len(positions)
        self._active_span = None
        return True

    def _reset_search(self, *_: object) -> None:
        self._matches = None
        self._current_index = -1
        self._active_span = None
        self._last_text = ""
        self._last_query = self._find_var.get()
        self._last_case_sensitive = self._case_sensitive_var.get()
        self._clear_highlight_callback()
        if self._last_query:
            self._status_var.set("Ready to search.")
        else:
            self._status_var.set("Enter search text.")
