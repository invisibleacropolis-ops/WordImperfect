# Engineer Guide

This guide provides implementation notes and ongoing context for contributors building WordImperfect. Update this document whenever architectural decisions are made, TODO items are identified, or progress metrics change.

## 1. Architectural Overview

- **Runtime:** Python 3.11+ is targeted for development to leverage recent language features and typing improvements.
- **Packaging:** The project uses the `src/` layout with [`setuptools`](https://setuptools.pypa.io/) metadata defined in `pyproject.toml`. The primary package is `wordimperfect`.
- **Testing:** `pytest` is the default test runner. Tests live under `tests/` and mirror the module structure. GitHub Actions executes the suite on pushes and pull requests.
- **Tooling:** Code formatting uses `black` and import sorting uses `isort`. Static analysis leverages `ruff` for linting and `mypy` for strict typing feedback.
- **Packaging:** Desktop builds are automated through PyInstaller (`packaging/wordimperfect.spec`).
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
| 2024-06-10 | Added GitHub Actions CI for Ruff, mypy, and pytest. | Ensures continuous linting and testing on every change. | ✅ Active |
| 2024-06-10 | Authored PyInstaller spec + release profile. | Enables reproducible desktop bundles during releases. | ✅ Active |

## 3. Workflow Backlog (Prioritised)

| Priority | Item | % Complete | Notes |
|----------|------|------------|-------|
| P0 | Document the baseline writing workflow, document lifecycle, and essential formatting scope. | 100% | Workflow guide published in `docs/writing-workflow.md`; future edits will track new features as they land. |
| P1 | Flesh out the GUI requirements and asset pipeline. | 95% | `docs/architecture.md` now details window layout, event lifecycle, theming presets, the baseline icon catalogue, and a PyInstaller validation checklist covering asset bundles. Final verification will come from the first packaged release. |
| P1 | Document the data model and persistence strategy (if any). | 95% | `docs/data-model.md` captures controllers, in-memory state, and the JSON sidecar used to persist paragraph styles; remaining work is folding the metadata into native `.rtf`/`.docx` payloads. |
| P2 | Populate `docs/` with technical references and design drafts. | 100% | `docs/technical-reference.md` now outlines controllers/services, GUI composition, and the PyInstaller packaging spec. Future edits will expand as new modules land. |
| P2 | Persist per-paragraph styling metadata for richer round-tripping. | 75% | Paragraph styles now round-trip via `FileService` JSON sidecars; future enhancements will embed formatting directly in `.rtf`/`.docx`. |
| P3 | Extend find/replace UX to support match highlighting and incremental navigation. | 100% | Added a dedicated `FindReplaceDialog` with case sensitivity toggles, incremental navigation, replace-all, and global `F3` shortcuts backed by `EditingController`. |
| P3 | Attach rendering logic for object handlers beyond textual placeholders (e.g., true image embedding). | 0% | Requires asset loading strategy. |

Progress percentages help stage multi-session work; update them after each sprint or notable milestone.

## 4. Progress Metrics

| Metric | Current Status |
|--------|----------------|
| Code coverage | Not yet tracked (suite expanded with controller + styling tests) |
| Automated tests | Functional unit coverage for document, formatting, editing, insertion, and styling helpers; CI enforces pytest |
| Linting | Configured (`ruff`, `black`, `isort`, `mypy`) and enforced in CI |
| Releases | None yet (see `CHANGELOG.md`); PyInstaller spec ready |

## 5. Versioning & Release Workflow

- **Versioning Strategy:** Semantic Versioning (`MAJOR.MINOR.PATCH`). Increment `MINOR` for new features, `PATCH` for fixes, and `MAJOR` for breaking API/UX changes.
- **Version Sources:** Update `project.version` in `pyproject.toml` and `__version__` in `wordimperfect/__init__.py` together.

### Release Checklist

1. Review backlog for completed items and capture them in `CHANGELOG.md`.
2. Bump the semantic version in `pyproject.toml` and `wordimperfect/__init__.py`.
3. Run local quality gates:
   - `ruff check .`
   - `mypy`
   - `pytest`
4. Build the distributable bundle:
   - `python -m pip install -e .[release]`
   - `pyinstaller packaging/wordimperfect.spec`
5. Smoke test the generated app in `dist/wordimperfect/`.
6. Create a signed tag (`git tag -s vX.Y.Z`) and push tags to origin.
7. Draft the GitHub release attaching the bundled artifacts.

Document any deviations or special steps in this guide after the release completes.

## 6. WordPad Feature Set Implementation

### Inline and Paragraph Styling

- `FormattingController` now models font family/size, foreground colour, inline toggles, alignment, indent, and list types. Logic is pure Python, enabling granular unit tests (`tests/test_controllers_logic.py`).
- `TextStyler` adapts controller state into Tk text widget mutations. It confines Tk-specific calls (tags, configuration, and list prefixing) to a single helper so the GUI remains thin. Tests rely on a light-weight fake widget to validate behaviour without requiring a display server.
- **Rationale:** Keeping formatting state and Tk mutations separate allows richer automation/tests and positions us for alternative front-ends if needed.
- **Gaps:** Paragraph styles now persist via JSON sidecars handled by `FileService`; the remaining work is translating that metadata into native `.rtf` control words/`.docx` XML so external editors can consume it directly.

### Editing Utilities

- `EditingController` exposes search helpers (`find_occurrences()`, `find_matches()`, `next_occurrence()`) and replacement utilities. A dedicated `FindReplaceDialog` now manages the workflow with case-sensitive toggles, incremental navigation buttons, replace-all, and shared `F3`/`Shift+F3` accelerators for quick iteration.
- **Rationale:** Centralising search logic keeps the GUI declarative and simplifies future additions (regex, search history, etc.) while the dialog concentrates Tk widget state and callbacks.
- **Gaps:** Regex searches and persistent history are still open questions once we broaden the editing feature set.

### Object Insertion

- `ObjectInsertionController` registers handlers keyed by human-friendly labels. The Tk "Insert" menu is populated dynamically from this registry; an image placeholder handler ships by default.
- **Rationale:** Editors frequently need bespoke embedded content. Delegating to handlers keeps the core unaware of concrete object types while enabling plugin-like extensibility.
- **Gaps:** Current image insertion inserts text placeholders only. Hooking up actual image rendering (e.g., with `PhotoImage`) and persistence is still outstanding.

### Testing Notes

- Added unit coverage around formatting toggles, search helpers, object insertion, and the styling adapter. A fake text widget enables deterministic assertions without invoking Tk.
- Future integration work should continue to exercise GUI flows via focused helpers rather than end-to-end Tk sessions to avoid headless environment issues.

## 7. Contributor Notes

- When adding new modules, include docstrings and type annotations to aid discoverability.
- Update this guide with major architectural changes or new tooling decisions.
- Keep `CHANGELOG.md` synchronized with releases or notable milestones.

