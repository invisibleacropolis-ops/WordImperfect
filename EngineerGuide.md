# Engineer Guide

This guide provides implementation notes and ongoing context for contributors building WordImperfect. Update this document whenever architectural decisions are made, TODO items are identified, or progress metrics change.

## 1. Architectural Overview

- **Runtime:** Python 3.11+ is targeted for development to leverage recent language features and typing improvements.
- **Packaging:** The project uses the `src/` layout with [`setuptools`](https://setuptools.pypa.io/) metadata defined in `pyproject.toml`. The primary package is `wordimperfect`.
- **Testing:** `pytest` is the default test runner. Tests live under `tests/` and mirror the module structure.
- **Tooling:** Code formatting uses `black` and import sorting uses `isort`. Static analysis leverages `ruff` for linting to keep feedback fast.
- **Documentation:** High-level references live in `README.md`. Architecture notes, decision records, and progress metrics remain here. Long-form technical documents can be placed under `docs/` as the project evolves.

## 2. Decision Log

| Date       | Decision | Context | Status |
|------------|----------|---------|--------|
| 2024-05-06 | Adopted `src/` layout with `pyproject.toml` build backend. | Facilitates clean packaging and aligns with modern Python practices. | ✅ Active |
| 2024-05-06 | Standardized tooling on Black, isort, and Ruff. | Provides consistent formatting and linting with minimal configuration overhead. | ✅ Active |
| 2024-05-06 | Established placeholder test `test_scaffolding.py`. | Ensures CI executes at least one test and validates tooling setup. | ✅ Active |
| 2024-06-03 | Implemented WordPad-formatting controllers and Tkinter styling layer. | Adds font, colour, paragraph, and list management without tying logic to widgets. | ✅ Active |
| 2024-06-03 | Added editing search utilities and find/replace UX. | Centralises text search logic and surfaces it through the Tk toolbar/menu. | ✅ Active |
| 2024-06-03 | Introduced pluggable object insertion registry. | Provides extensible hooks for embedding images and future OLE-like payloads. | ✅ Active |

## 3. TODO Backlog

- Define the initial game specification, including rules and core mechanics.
- Flesh out the GUI requirements and asset pipeline.
- Add continuous integration workflows for testing and linting.
- Document the data model and persistence strategy (if any).
- Populate `docs/` with technical references and design drafts.
- Attach rendering logic for object handlers beyond textual placeholders (e.g., true image embedding with Tk `PhotoImage`).
- Persist per-paragraph styling metadata for richer round-tripping (currently tags are applied only in-memory).
- Extend find/replace UX to support match highlighting and incremental navigation.

## 4. Progress Metrics

| Metric | Current Status |
|--------|----------------|
| Code coverage | Not yet tracked (suite expanded with controller + styling tests) |
| Automated tests | Functional unit coverage for document, formatting, editing, insertion, and styling helpers |
| Linting | Configured (`ruff`, `black`, `isort`) |
| Releases | None yet (see `CHANGELOG.md`) |

## 5. WordPad Feature Set Implementation

### Inline and Paragraph Styling

- `FormattingController` now models font family/size, foreground colour, inline toggles, alignment, indent, and list types. Logic is pure Python, enabling granular unit tests (`tests/test_controllers_logic.py`).
- `TextStyler` adapts controller state into Tk text widget mutations. It confines Tk-specific calls (tags, configuration, and list prefixing) to a single helper so the GUI remains thin. Tests rely on a light-weight fake widget to validate behaviour without requiring a display server.
- **Rationale:** Keeping formatting state and Tk mutations separate allows richer automation/tests and positions us for alternative front-ends if needed.
- **Gaps:** Styling changes are applied in-memory only. Persisting styles back to `.rtf`/`.docx` will need future work in the file service layer.

### Editing Utilities

- `EditingController` exposes `find_occurrences` and `replace` helpers, returning deterministic summaries. The Tk menu now provides a modal find/replace flow using these utilities.
- **Rationale:** Centralising search logic keeps the GUI declarative and simplifies future additions (regex, case sensitivity toggles, etc.).
- **Gaps:** The dialog remains minimal—no incremental highlighting, replace-next semantics, or history.

### Object Insertion

- `ObjectInsertionController` registers handlers keyed by human-friendly labels. The Tk "Insert" menu is populated dynamically from this registry; an image placeholder handler ships by default.
- **Rationale:** Editors frequently need bespoke embedded content. Delegating to handlers keeps the core unaware of concrete object types while enabling plugin-like extensibility.
- **Gaps:** Current image insertion inserts text placeholders only. Hooking up actual image rendering (e.g., with `PhotoImage`) and persistence is still outstanding.

### Testing Notes

- Added unit coverage around formatting toggles, search helpers, object insertion, and the styling adapter. A fake text widget enables deterministic assertions without invoking Tk.
- Future integration work should continue to exercise GUI flows via focused helpers rather than end-to-end Tk sessions to avoid headless environment issues.

## 6. Contributor Notes

- When adding new modules, include docstrings and type annotations to aid discoverability.
- Update this guide with major architectural changes or new tooling decisions.
- Keep `CHANGELOG.md` synchronized with releases or notable milestones.

