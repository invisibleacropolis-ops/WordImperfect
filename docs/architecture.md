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

#### Theming presets

- **Preset catalog** – `assets/themes/` stores JSON presets under filenames such as `light.json`, `dark.json`, and `high-contrast.json`.
  Each preset defines Tk/ttk style names, palette values, and toolbar icon tint rules. A future `ThemeService` will enumerate files in
  this folder at startup to populate a "Theme" submenu.
- **Runtime application** – Theme activation flows through a dedicated helper (`wordimperfect.app.apply_theme`) that binds palette colours
  to ttk style maps. Controllers remain unaware of theme selection; widgets receive style changes via Tk variable traces.
- **Extensibility** – Third-party themes can be dropped into `assets/themes/` without code changes provided they expose the `base`,
  `accent`, and `surface` colour keys plus typography overrides (`font_family`, `font_size`). Invalid files are ignored with a warning to
  keep the UX resilient.

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

#### Icon catalogue

The application surface references the following baseline icons. Designers should export assets at 1x, 1.5x, and 2x scale to balance crispness
across common display densities. All icons live under `assets/icons/` and share a monochrome SVG source for theming tinting.

| Identifier | Usage | File name | Notes |
|------------|-------|-----------|-------|
| `document-new` | Toolbar "New" button | `assets/icons/document-new.svg` | Neutral outline that reads well when tinted accent colour. |
| `document-open` | Toolbar "Open" button | `assets/icons/document-open.svg` | Folder with up arrow to imply import. |
| `document-save` | Toolbar "Save" button | `assets/icons/document-save.svg` | Modernised diskette outline retained for recognisability. |
| `format-bold` | Inline formatting toggle | `assets/icons/format-bold.svg` | Render the glyph at 14pt weight to match Tk default sizing. |
| `format-italic` | Inline formatting toggle | `assets/icons/format-italic.svg` | Ensure slant is at least 12° for clarity. |
| `format-underline` | Inline formatting toggle | `assets/icons/format-underline.svg` | Align underline stroke with Tk baseline metrics. |
| `format-align-left` | Paragraph alignment | `assets/icons/format-align-left.svg` | Use consistent bar spacing across all alignment icons. |
| `format-align-center` | Paragraph alignment | `assets/icons/format-align-center.svg` | |
| `format-align-right` | Paragraph alignment | `assets/icons/format-align-right.svg` | |
| `format-list-bullet` | List toggle | `assets/icons/format-list-bullet.svg` | Circular bullets sized to 3px radius at 1x scale. |
| `format-list-numbered` | List toggle | `assets/icons/format-list-numbered.svg` | Reserve margin for double-digit markers. |
| `search` | Find/replace dialog | `assets/icons/search.svg` | Magnifier sized for 16px square button. |
| `replace` | Find/replace dialog | `assets/icons/replace.svg` | Pair with search icon to convey bidirectional flow. |

## Quality Tooling

- Continuous testing via `pytest` with configuration in `pyproject.toml`.
- Linting and static analysis through Ruff (`ruff check .`) and mypy (`mypy`).
- GitHub Actions workflow `.github/workflows/ci.yml` executes linting and tests on pushes and pull requests.

## Packaging

`packaging/wordimperfect.spec` packages the application into a distributable folder using PyInstaller. Assets under `assets/` are
included automatically when present.
