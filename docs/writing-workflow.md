# Writing Workflow Guide

This guide explains the baseline WordImperfect authoring experience so outside engineers can understand how the GUI and controllers collaborate to manage a document's lifecycle and formatting capabilities. It focuses on the default desktop workflow exposed by `wordimperfect.app` and the controllers in `wordimperfect.controllers`.

## 1. Launching the Editor

1. Install the project in editable mode (`python -m pip install -e .`).
2. Start the Tkinter entry point via `python -m wordimperfect.app`.
3. The main window opens with a blank document, formatting toolbar, and status area ready for input.

## 2. Document Lifecycle

WordImperfect currently supports plaintext workflows tuned for rapid drafting. The `File` menu orchestrates the lifecycle operations:

| Action | UI Path | Backing Components | Notes |
|--------|---------|--------------------|-------|
| New | `File → New` | `DocumentController.new_document()` | Clears the workspace, resets formatting state, and primes controllers for fresh content. Unsaved changes trigger a confirmation dialog. |
| Open… | `File → Open…` | `FileService.open_file()` feeding `DocumentController.load()` | Loads `.txt` files into the text widget. Formatting metadata is reinitialised to defaults pending future persistence work. |
| Save | `File → Save` | `FileService.save()` driven by `DocumentController.snapshot()` | Writes the in-memory buffer to disk. For first-time saves the user is prompted for a file path. |
| Save As… | `File → Save As…` | Same as **Save** but always prompts for a destination | Supports branching copies and format conversions once additional serializers exist. |
| Close | Window chrome / `File → Exit` | `DocumentController.close()` | Gracefully shuts down after confirming whether unsaved work should be preserved. |

Future storage back-ends (e.g., `.rtf`, `.docx`) will slot into `FileService` while reusing the same controller orchestration.

## 3. Baseline Editing Flow

The editing loop is designed for fast iteration while keeping operations deterministic and testable:

1. Type directly into the main text area. `TextStyler` applies controller-driven tags to the Tk widget to reflect formatting state.
2. Use standard shortcuts for clipboard operations (Ctrl/Cmd + C/X/V). Event bindings are in `wordimperfect.app.shortcuts` to keep platform-specific tweaks centralised.
3. Invoke `Edit → Find & Replace…` to open the modal search dialog. This dialog wraps `EditingController.find_occurrences()` and `EditingController.replace()` so replacements can be unit tested independently of Tk.
4. Undo/redo is currently limited to Tk's built-in buffer. Extended history management is earmarked for a later milestone.

## 4. Essential Formatting Scope

The formatting toolbar highlights the supported styling primitives. Each control manipulates the shared `FormattingController` state before `TextStyler` applies the change to the selection or caret position.

| Control Group | UI Elements | Controller Responsibilities | Behaviour |
|---------------|-------------|-----------------------------|-----------|
| Font | Font family dropdown, size spinner | `FormattingController.set_font_family()` / `.set_font_size()` | Applies inline font changes by tagging the selected range. |
| Emphasis | Bold, Italic, Underline toggles | `.toggle_bold()`, `.toggle_italic()`, `.toggle_underline()` | Toggles boolean flags and re-renders the current selection. |
| Colour | Foreground colour picker | `.set_foreground_colour()` | Applies colour tags using Tk colour strings (e.g., `#RRGGBB`). |
| Alignment | Left, Centre, Right, Justify buttons | `.set_alignment()` | Adjusts paragraph-level alignment tags. |
| Indentation & Lists | Increase/decrease indent buttons, bullet/number list toggles | `.set_indent_level()`, `.set_list_style()` | Maintains per-paragraph metadata for indentation depth and list type. |

These primitives align with the controllers' unit tests in `tests/test_controllers_logic.py`, ensuring UI triggers match the documented behaviour.

## 5. Object Insertion

`Insert → Image Placeholder` demonstrates the pluggable object pipeline. Selecting the command calls `ObjectInsertionController.insert("Image Placeholder")`, which dispatches to the registered handler. The default handler inserts a descriptive token into the document while reserving space for future embedded rendering.

Engineers can register additional handlers by calling `ObjectInsertionController.register(label, handler)` during application start-up.

## 6. Extending the Workflow

Outside engineers extending the workflow should:

- Update `docs/writing-workflow.md` with new lifecycle or formatting primitives so the baseline documentation remains authoritative.
- Add controller-level unit tests alongside GUI changes to keep behaviour reproducible.
- Note major milestones or percentage changes in `EngineerGuide.md` to reflect backlog progress.

This documentation now completes the baseline writing workflow coverage requested in the engineering backlog.
