"""Tkinter front-end for the WordImperfect editor."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

from wordimperfect.controllers import (
    Alignment,
    DocumentController,
    EditingController,
    FormattingController,
    ListType,
    ObjectInsertionController,
    TextStyler,
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
        self._object_controller = ObjectInsertionController()

        self._text = tk.Text(self._root, wrap="word", undo=True)
        self._status_var = tk.StringVar(value="Ready")
        self._bold_var = tk.BooleanVar(value=False)
        self._italic_var = tk.BooleanVar(value=False)
        self._underline_var = tk.BooleanVar(value=False)
        state = self._formatting_controller.state
        self._font_var = tk.StringVar(value=state.font_family)
        self._size_var = tk.StringVar(value=str(state.font_size))
        self._color_var = tk.StringVar(value=state.foreground)
        self._list_var = tk.StringVar(value=state.list_type.value)
        self._suspend_modified_event = False
        self._styler = TextStyler(self._text)
        self._insert_menu: tk.Menu | None = None

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
        file_menu.add_command(
            label="New", accelerator="Ctrl+N", command=self._new_document
        )
        file_menu.add_command(
            label="Open…", accelerator="Ctrl+O", command=self._open_document
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save", accelerator="Ctrl+S", command=self._save_document
        )
        file_menu.add_command(
            label="Save As…", accelerator="Ctrl+Shift+S", command=self._save_document_as
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(
            label="Undo", accelerator="Ctrl+Z", command=self._text.edit_undo
        )
        edit_menu.add_command(
            label="Redo", accelerator="Ctrl+Y", command=self._text.edit_redo
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Cut",
            accelerator="Ctrl+X",
            command=lambda: self._root.event_generate("<<Cut>>"),
        )
        edit_menu.add_command(
            label="Copy",
            accelerator="Ctrl+C",
            command=lambda: self._root.event_generate("<<Copy>>"),
        )
        edit_menu.add_command(
            label="Paste",
            accelerator="Ctrl+V",
            command=lambda: self._root.event_generate("<<Paste>>"),
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Select All", accelerator="Ctrl+A", command=self._select_all
        )
        edit_menu.add_command(
            label="Find && Replace…",
            accelerator="Ctrl+F",
            command=self._open_find_replace,
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)

        insert_menu = tk.Menu(menubar, tearoff=False)
        self._insert_menu = insert_menu
        self._object_controller.register_handler("Image…", self._insert_image)
        self._rebuild_insert_menu()
        menubar.add_cascade(label="Insert", menu=insert_menu)

        self._root.config(menu=menubar)

        self._root.bind_all("<Control-n>", lambda event: self._new_document())
        self._root.bind_all("<Control-o>", lambda event: self._open_document())
        self._root.bind_all("<Control-s>", lambda event: self._save_document())
        self._root.bind_all("<Control-S>", lambda event: self._save_document_as())
        self._root.bind_all("<Control-f>", lambda event: self._open_find_replace())

    def _build_toolbar(self) -> None:
        toolbar = ttk.Frame(self._root, padding=(4, 2))
        font_choices = ("Arial", "Courier New", "Helvetica", "Times New Roman")
        font_box = ttk.Combobox(
            toolbar, textvariable=self._font_var, values=font_choices, width=18
        )
        font_box.bind("<<ComboboxSelected>>", lambda event: self._change_font_family())

        size_choices = ("8", "10", "12", "14", "18", "24", "32")
        size_box = ttk.Combobox(
            toolbar,
            textvariable=self._size_var,
            values=size_choices,
            width=4,
        )
        size_box.bind("<<ComboboxSelected>>", lambda event: self._change_font_size())

        color_btn = ttk.Button(toolbar, text="Color", command=self._choose_color)

        bold_btn = ttk.Checkbutton(
            toolbar, text="Bold", variable=self._bold_var, command=self._toggle_bold
        )
        italic_btn = ttk.Checkbutton(
            toolbar,
            text="Italic",
            variable=self._italic_var,
            command=self._toggle_italic,
        )
        underline_btn = ttk.Checkbutton(
            toolbar,
            text="Underline",
            variable=self._underline_var,
            command=self._toggle_underline,
        )

        align_left = ttk.Button(
            toolbar, text="Left", command=lambda: self._set_alignment(Alignment.LEFT)
        )
        align_center = ttk.Button(
            toolbar,
            text="Center",
            command=lambda: self._set_alignment(Alignment.CENTER),
        )
        align_right = ttk.Button(
            toolbar, text="Right", command=lambda: self._set_alignment(Alignment.RIGHT)
        )

        indent_decrease = ttk.Button(
            toolbar, text="Indent -", command=self._decrease_indent
        )
        indent_increase = ttk.Button(
            toolbar, text="Indent +", command=self._increase_indent
        )

        list_box = ttk.Combobox(
            toolbar,
            textvariable=self._list_var,
            values=[
                ListType.NONE.value,
                ListType.BULLET.value,
                ListType.NUMBERED.value,
            ],
            width=9,
            state="readonly",
        )
        list_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self._set_list_type(self._list_var.get()),
        )
        clear_list_btn = ttk.Button(
            toolbar, text="Clear List", command=self._clear_list_type
        )

        widgets = [
            font_box,
            size_box,
            color_btn,
            bold_btn,
            italic_btn,
            underline_btn,
            align_left,
            align_center,
            align_right,
            indent_decrease,
            indent_increase,
            list_box,
            clear_list_btn,
        ]
        for column, widget in enumerate(widgets):
            widget.grid(row=0, column=column, padx=3)

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
        self._apply_formatting()
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
        self._apply_formatting()
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
        filename = filedialog.asksaveasfilename(
            filetypes=filetypes, defaultextension=".rtf"
        )
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
        self._apply_formatting()
        self._update_status()

    def _change_font_family(self) -> None:
        family = self._font_var.get()
        self._formatting_controller.set_font_family(family)
        self._apply_formatting()
        self._update_status()

    def _change_font_size(self) -> None:
        try:
            size = int(self._size_var.get())
        except (ValueError, tk.TclError):
            return
        self._formatting_controller.set_font_size(size)
        self._apply_formatting()
        self._update_status()

    def _choose_color(self) -> None:
        color = colorchooser.askcolor(color=self._color_var.get())[1]
        if not color:
            return
        self._color_var.set(color)
        self._formatting_controller.set_foreground(color)
        self._apply_formatting()
        self._update_status()

    def _set_alignment(self, alignment: Alignment) -> None:
        self._formatting_controller.set_alignment(alignment)
        self._apply_formatting()
        self._update_status()

    def _increase_indent(self) -> None:
        self._formatting_controller.increase_indent()
        self._apply_formatting()
        self._update_status()

    def _decrease_indent(self) -> None:
        self._formatting_controller.decrease_indent()
        self._apply_formatting()
        self._update_status()

    def _set_list_type(self, list_type: str) -> None:
        self._formatting_controller.set_list_type(list_type)
        self._apply_formatting()
        self._update_status()

    def _clear_list_type(self) -> None:
        self._formatting_controller.clear_list_type()
        self._list_var.set(ListType.NONE.value)
        self._apply_formatting()
        self._update_status()

    def _on_text_modified(
        self, event: tk.Event[tk.Widget]
    ) -> None:  # pragma: no cover - Tkinter event signature
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
        if (
            not self._document_controller.metadata.is_modified
            and not self._text.edit_modified()
        ):
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
            for name, active in (
                ("B", state.bold),
                ("I", state.italic),
                ("U", state.underline),
            )
            if active
        ]
        inline = "None" if not flags else " ".join(flags)
        parts = [
            f"Font: {state.font_family} {state.font_size}",
            f"Color: {state.foreground}",
            f"Inline: {inline}",
            f"Align: {state.alignment.value.capitalize()}",
            f"Indent: {state.indent}",
            f"List: {state.list_type.value.capitalize()}",
        ]
        return "  ".join(parts)

    def _update_status(self) -> None:
        text = self._text.get("1.0", "end-1c")
        summary = self._editing_controller.summarize(text)
        formatting = self._formatting_status()
        counts = (
            f"Chars: {summary.characters}  "
            f"Words: {summary.words}  "
            f"Lines: {summary.lines}"
        )
        message = f"{counts}  |  {formatting}"
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
        self._font_var.set(state.font_family)
        self._size_var.set(str(state.font_size))
        self._color_var.set(state.foreground)
        self._list_var.set(state.list_type.value)

    @contextmanager
    def _suspend_modified_tracking(self) -> Iterator[None]:
        self._suspend_modified_event = True
        try:
            yield
        finally:
            self._suspend_modified_event = False

    def _apply_formatting(self) -> None:
        self._styler.apply(self._formatting_controller.state)

    def _open_find_replace(self) -> None:
        query = simpledialog.askstring("Find", "Text to find:")
        if query is None:
            return
        replacement = simpledialog.askstring(
            "Replace", "Replace with:", initialvalue=""
        )
        if replacement is None:
            return
        content = self._text.get("1.0", "end-1c")
        summary = self._editing_controller.replace(content, query, replacement)
        if summary.replacements:
            with self._suspend_modified_tracking():
                self._text.delete("1.0", tk.END)
                self._text.insert("1.0", summary.text)
            self._document_controller.mark_modified()
            self._text.edit_modified(True)
            self._update_status()
        messagebox.showinfo(
            "Find & Replace", f"Replaced {summary.replacements} occurrence(s)."
        )

    def _insert_image(self) -> None:
        filename = filedialog.askopenfilename(
            title="Insert Image",
            filetypes=(
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*"),
            ),
        )
        if not filename:
            return
        placeholder = f"[Image: {Path(filename).name}]"
        self._text.insert(tk.INSERT, placeholder)
        self._document_controller.mark_modified()
        self._update_status()

    def _rebuild_insert_menu(self) -> None:
        if self._insert_menu is None:
            return
        self._insert_menu.delete(0, tk.END)
        for name in self._object_controller.available_objects():
            self._insert_menu.add_command(
                label=name, command=self._make_insert_command(name)
            )

    def _make_insert_command(self, name: str) -> Callable[[], None]:
        def callback() -> None:
            self._object_controller.insert(name)

        return callback

    def register_object_handler(
        self, name: str, handler: Callable[..., object]
    ) -> None:
        """Allow plugins to publish additional insertable objects."""

        self._object_controller.register_handler(name, handler)
        self._rebuild_insert_menu()


__all__ = ["Application"]
