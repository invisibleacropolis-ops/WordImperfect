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

## Quality Tooling

- Continuous testing via `pytest` with configuration in `pyproject.toml`.
- Linting and static analysis through Ruff (`ruff check .`) and mypy (`mypy`).
- GitHub Actions workflow `.github/workflows/ci.yml` executes linting and tests on pushes and pull requests.

## Packaging

`packaging/wordimperfect.spec` packages the application into a distributable folder using PyInstaller. Assets under `assets/` are
included automatically when present.
