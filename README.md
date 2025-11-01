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
2. Run the automated tests to verify the environment:
   ```bash
   pytest
   ```

Additional workflow details, architecture decisions, and open tasks are tracked in `EngineerGuide.md`.
