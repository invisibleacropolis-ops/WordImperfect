# WordImperfect

WordImperfect is an experimental platform for exploring imperfect information word-based games. This repository currently provides the foundational project scaffolding so future contributors can focus on implementing gameplay mechanics, AI opponents, and graphical interfaces.

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

### Building a Desktop Bundle

Use the provided PyInstaller specification to produce a distributable desktop folder:

```bash
python -m pip install -e .[release]
pyinstaller packaging/wordimperfect.spec
```

The resulting bundle will be placed under `dist/wordimperfect/`.

Additional workflow details, architecture decisions, release process, and open tasks are tracked in `EngineerGuide.md`.
