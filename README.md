
# WordImperfect

WordImperfect is a focused desktop word processor designed for fast drafting, rich formatting, and lightweight document management. This repository provides the foundational project scaffolding so contributors can concentrate on editing features, file interoperability, and a polished writing workflow.

## Project Layout

```
WordImperfect/
├── assets/          # GUI imagery, fonts, and audio assets
├── docs/            # Long-form documentation, specs, and references
├── src/             # Python source code (packaged under `wordimperfect`)
├── tests/           # Automated tests covering the `wordimperfect` package
├── CHANGELOG.md     # Version history and release notes
├── EngineerGuide.md # Architecture decisions, TODOs, and progress metrics
└── README.md        # High-level overview and onboarding information
```

## Getting Started

1. Install the project in editable mode:
   ```bash
   python -m pip install -e .
   ```
2. Install the development tooling (optional but recommended for contributors):
   ```bash
   python -m pip install -e .[dev]
   ```
3. Run the automated tests to verify the environment:
   ```bash
   pytest
   ```

### Quality Checks

- Ruff linting:
  ```bash
  ruff check .
  ```
- Static type analysis (mypy):
  ```bash
  mypy
  ```

## Using WordImperfect

WordImperfect centers around a single document workspace tailored to drafting and revising text-heavy files. Key concepts:

- **Document lifecycle:** Use *File → New* to start a blank document, *File → Open…* to load an existing `.txt`, and the *Save*/*Save As…* actions to persist changes. Unsaved changes trigger a prompt before closing.
- **Formatting controls:** The toolbar exposes font family, size, colour, bold, italic, underline, alignment, indentation, and list styling. Selection-sensitive toggles update automatically when the caret moves into styled regions.
- **Editing utilities:** Standard clipboard shortcuts are available along with a *Find & Replace…* dialog powered by the editing controllers for deterministic replacements.
- **Object insertion:** The *Insert* menu provides extensible hooks, currently shipping with image placeholder insertion for drafting layouts that will later include media.

Additional guides for advanced workflows live in `docs/` as they are produced. See [`docs/writing-workflow.md`](docs/writing-workflow.md) for a detailed walkthrough of the baseline authoring lifecycle, editing loop, and formatting capabilities.

### Building a Desktop Bundle

Use the provided PyInstaller specification to produce a distributable desktop folder:

```bash
python -m pip install -e .[release]
pyinstaller packaging/wordimperfect.spec
```

The resulting bundle will be placed under `dist/wordimperfect/`.

Additional workflow details, architecture decisions, release process, and open tasks are tracked in `EngineerGuide.md`.

