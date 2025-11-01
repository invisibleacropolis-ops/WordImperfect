# Architecture Overview

This document accompanies `EngineerGuide.md` with a module-level reference for outside engineers. Update it when new packages or
subsystems are introduced.

## High-Level Components

- **`wordimperfect.app`** – Tkinter GUI bootstrapper responsible for menus, toolbars, and binding controllers to widget events.
- **`wordimperfect.controllers`** – Domain logic for formatting, editing, document persistence, and extensible object insertion.
- **`wordimperfect.services`** – Service abstractions such as `FileService` for reading/writing supported document formats.
- **`tests/`** – Pytest suites validating controller behaviour, styling interactions, and editor utilities.
- **`packaging/`** – Release automation assets including the PyInstaller specification.

## Runtime Notes

The GUI remains thin: controllers expose pure-Python state transitions, while `TextStyler` adapts them to Tk tags. This separation
keeps domain logic testable and makes alternative front-ends feasible.

### GUI Requirements

- **Primary window** – `wordimperfect.app.Application` builds a single Tk root sized to `900x600` with a text widget (`tk.Text`) as the
  editing surface. All controller state is configured during initialisation so the UI can be recreated programmatically.
- **Menu system** – File/Edit/Insert menus are constructed from controller commands. Every action is paired with a keyboard
  accelerator (`<Control-*>` bindings) to keep the workflow accessible on Windows, macOS, and Linux. Insert menu entries are
  regenerated whenever plugins register new object handlers.
- **Toolbar** – A single-row ttk toolbar exposes font family/size selectors, colour picker, inline toggle buttons, alignment
  buttons, indent adjustments, and list controls. Widgets read/write controller-backed Tk variables so the UI stays in sync when
  formatting changes are driven programmatically (e.g., via future scripting APIs).
- **Status bar** – A ttk label at the window footer shows live document metrics (`EditingController.summarize`) alongside inline
  formatting state. Modified documents append a `(modified)` tag that mirrors window-title behaviour.
- **Event lifecycle** – Editing operations that mutate the document wrap Tk calls inside `_suspend_modified_tracking()` to avoid
  recursive `<<Modified>>` notifications. New GUI features should follow this pattern whenever they perform scripted edits.

### Asset Pipeline

- **Source of truth** – All distributable imagery, icons, and configuration live in `assets/`. The directory is empty by default to
  keep the repo lightweight; designers can add subfolders (e.g., `assets/icons/`, `assets/themes/`).
- **Runtime loading** – Assets are accessed via `pathlib.Path` lookups relative to `Application`'s module directory. Avoid using
  working-directory assumptions so packaged builds resolve resources correctly.
- **Build integration** – `packaging/wordimperfect.spec` automatically bundles the entire `assets/` tree into PyInstaller builds. Any
  new asset types should be added here if they need special handling (e.g., fonts requiring registration on startup).
- **Theming** – Tk/ttk styling is centralised in the toolbar creation logic; introducing additional themes should define ttk style
  configuration helpers and ship associated palette files under `assets/themes/`. Document new style toggles alongside the toolbar
  notes above when adding them.

## Quality Tooling

- Continuous testing via `pytest` with configuration in `pyproject.toml`.
- Linting and static analysis through Ruff (`ruff check .`) and mypy (`mypy`).
- GitHub Actions workflow `.github/workflows/ci.yml` executes linting and tests on pushes and pull requests.

## Packaging

`packaging/wordimperfect.spec` packages the application into a distributable folder using PyInstaller. Assets under `assets/` are
included automatically when present.
