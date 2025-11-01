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

## 3. TODO Backlog

- Define the initial game specification, including rules and core mechanics.
- Flesh out the GUI requirements and asset pipeline.
- Add continuous integration workflows for testing and linting.
- Document the data model and persistence strategy (if any).
- Populate `docs/` with technical references and design drafts.

## 4. Progress Metrics

| Metric | Current Status |
|--------|----------------|
| Code coverage | N/A (placeholder tests only) |
| Automated tests | 1 placeholder test (`tests/test_scaffolding.py`) |
| Linting | Configured (`ruff`, `black`, `isort`) |
| Releases | None yet (see `CHANGELOG.md`) |

## 5. Contributor Notes

- When adding new modules, include docstrings and type annotations to aid discoverability.
- Update this guide with major architectural changes or new tooling decisions.
- Keep `CHANGELOG.md` synchronized with releases or notable milestones.

