"""Tkinter front-end for the WordImperfect editor."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from wordimperfect.controllers import (
    DocumentController,
    EditingController,
    FormattingController,
)
from wordimperfect.services import FileService


class Application:
    """Bootstrap the Tkinter user interface."""

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("WordImperfect")
        self._root.geometry("900x600")

        self._file_service = FileService()
        self._document_controller = DocumentController(self._file_service)
        self._editing_controller = EditingController()
        self._formatting_controller = FormattingController()

        self._text = tk.Text(self._root, wrap="word", undo=True)
        self._status_var = tk.StringVar(value="Ready")
        self._bold_var = tk.BooleanVar(value=False)
        self._italic_var = tk.BooleanVar(value=False)
        self._underline_var = tk.BooleanVar(value=False)
        self._suspend_modified_event = False

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._build_status_bar()

        self._text.bind("<<Modified>>", self._on_text_modified)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._update_title()
        self._update_status()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self._root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self._new_document)
        file_menu.add_command(label="Open…", accelerator="Ctrl+O", command=self._open_document)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self._save_document)
        file_menu.add_command(
            label="Save As…", accelerator="Ctrl+Shift+S", command=self._save_document_as
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self._text.edit_undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self._text.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self._root.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self._root.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self._root.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self._select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self._root.config(menu=menubar)

        self._root.bind_all("<Control-n>", lambda event: self._new_document())
        self._root.bind_all("<Control-o>", lambda event: self._open_document())
        self._root.bind_all("<Control-s>", lambda event: self._save_document())
        self._root.bind_all("<Control-S>", lambda event: self._save_document_as())

    def _build_toolbar(self) -> None:
        toolbar = ttk.Frame(self._root, padding=(4, 2))
        bold_btn = ttk.Checkbutton(toolbar, text="Bold", variable=self._bold_var, command=self._toggle_bold)
        italic_btn = ttk.Checkbutton(toolbar, text="Italic", variable=self._italic_var, command=self._toggle_italic)
        underline_btn = ttk.Checkbutton(
            toolbar, text="Underline", variable=self._underline_var, command=self._toggle_underline
        )
        bold_btn.grid(row=0, column=0, padx=4)
        italic_btn.grid(row=0, column=1, padx=4)
        underline_btn.grid(row=0, column=2, padx=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self._toolbar = toolbar

    def _build_body(self) -> None:
        self._text.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)

    def _build_status_bar(self) -> None:
        status_bar = ttk.Label(self._root, textvariable=self._status_var, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._status_bar = status_bar

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------
    def _new_document(self) -> None:
        if not self._confirm_discard_changes():
            return
        self._document_controller.new_document()
        self._formatting_controller.reset()
        with self._suspend_modified_tracking():
            self._text.delete("1.0", tk.END)
        self._text.edit_modified(False)
        self._sync_formatting_vars()
        self._update_title()
        self._update_status()

    def _open_document(self) -> None:
        if not self._confirm_discard_changes():
            return
        filetypes = list(self._document_controller.supported_filetypes())
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if not filename:
            return
        path = Path(filename)
        text = self._document_controller.open_document(path)
        with self._suspend_modified_tracking():
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", text)
        self._text.edit_modified(False)
        self._formatting_controller.reset()
        self._sync_formatting_vars()
        self._update_title()
        self._update_status()

    def _save_document(self) -> None:
        try:
            if self._document_controller.metadata.path is None:
                self._save_document_as()
                return
            self._document_controller.save_document(self._text.get("1.0", "end-1c"))
            self._text.edit_modified(False)
            self._update_title()
            self._update_status()
        except ValueError:
            self._save_document_as()

    def _save_document_as(self) -> None:
        filetypes = list(self._document_controller.supported_filetypes())
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".rtf")
        if not filename:
            return
        path = Path(filename)
        content = self._text.get("1.0", "end-1c")
        self._document_controller.save_document(content, path)
        self._text.edit_modified(False)
        self._update_title()
        self._update_status()

    def _select_all(self) -> None:
        self._text.tag_add(tk.SEL, "1.0", tk.END)
        self._text.mark_set(tk.INSERT, "1.0")
        self._text.see(tk.INSERT)

    def _toggle_bold(self) -> None:
        self._formatting_controller.toggle_bold()
        self._sync_formatting_vars()
        self._update_status()

    def _toggle_italic(self) -> None:
        self._formatting_controller.toggle_italic()
        self._sync_formatting_vars()
        self._update_status()

    def _toggle_underline(self) -> None:
        self._formatting_controller.toggle_underline()
        self._sync_formatting_vars()
        self._update_status()

    def _on_text_modified(self, event: tk.Event[tk.Widget]) -> None:  # pragma: no cover - Tkinter event signature
        if self._suspend_modified_event:
            self._text.edit_modified(False)
            return
        if self._text.edit_modified():
            self._document_controller.mark_modified()
            self._update_title()
            self._update_status()
            self._text.edit_modified(False)

    def _on_close(self) -> None:
        if self._confirm_discard_changes():
            self._root.destroy()

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------
    def _confirm_discard_changes(self) -> bool:
        if not self._document_controller.metadata.is_modified and not self._text.edit_modified():
            return True
        response = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Save changes before continuing?",
            icon=messagebox.WARNING,
        )
        if response is None:
            return False
        if response:
            self._save_document()
            return not self._document_controller.metadata.is_modified
        return True

    def _formatting_status(self) -> str:
        state = self._formatting_controller.state
        flags = [
            name
            for name, active in (("B", state.bold), ("I", state.italic), ("U", state.underline))
            if active
        ]
        prefix = "Formatting: "
        return prefix + ("None" if not flags else " ".join(flags))

    def _update_status(self) -> None:
        text = self._text.get("1.0", "end-1c")
        summary = self._editing_controller.summarize(text)
        formatting = self._formatting_status()
        message = (
            f"Chars: {summary.characters}  Words: {summary.words}  Lines: {summary.lines}"
            f"  |  {formatting}"
        )
        if self._document_controller.metadata.is_modified:
            message += "  (modified)"
        self._status_var.set(message)

    def _update_title(self) -> None:
        title = f"WordImperfect - {self._document_controller.document_title()}"
        if self._document_controller.metadata.is_modified:
            title += "*"
        self._root.title(title)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Start the Tkinter main loop."""

        self._root.mainloop()

    def _sync_formatting_vars(self) -> None:
        state = self._formatting_controller.state
        self._bold_var.set(state.bold)
        self._italic_var.set(state.italic)
        self._underline_var.set(state.underline)

    @contextmanager
    def _suspend_modified_tracking(self) -> Iterator[None]:
        self._suspend_modified_event = True
        try:
            yield
        finally:
            self._suspend_modified_event = False


__all__ = ["Application"]

