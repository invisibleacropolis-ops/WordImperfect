# Data Model and Persistence Strategy

This reference explains the core in-memory models that power WordImperfect's controllers and how they map to the current
persistence layer. Use it when extending document storage or introducing richer formatting state.

## Document Metadata

- **`DocumentController`** encapsulates lifecycle coordination. It owns a `DocumentMetadata` dataclass composed of:
  - `path: Path | None` – absolute location of the file currently backing the workspace (or `None` when unsaved).
  - `is_modified: bool` – tracks whether user changes have diverged from the persisted contents.
- Controllers mutate the metadata via `mark_modified()`/`mark_clean()`. UI components read snapshots through the `metadata`
  property to update window titles and status surfaces.
- Supported formats are enumerated in `_SUPPORTED_FORMATS` so the GUI can present consistent file-dialog filters. Any new file
  types must be added both to this tuple and to the `FileService` implementations described below.

## Formatting State

- **`FormattingController`** manages inline and paragraph styling through the `FormattingState` dataclass. Key fields include font
  family/size, colour, boolean toggles for bold/italic/underline, paragraph alignment, indent depth, and active list type.
- All mutator methods (`toggle_bold()`, `set_font_family()`, `set_alignment()`, etc.) update the internal state and return the
  resolved value so GUI widgets can reflect the change immediately.
- `TextStyler.apply()` consumes a snapshot of `FormattingState` to configure Tk tags. Any additional formatting attribute should be
  captured in `FormattingState`, mutated through the controller, and translated inside `TextStyler` to keep presentation logic in a
  single location.
- **`ParagraphStyleSnapshot`** exposes paragraph-level formatting (alignment, indent, list type) for persistence. Controllers request
  a snapshot from `FormattingController.paragraph_style()` when paragraph metadata needs to be stored alongside document content.

## Paragraph styling metadata

- `DocumentMetadata` now contains a `paragraph_styles: dict[int, ParagraphStyleSnapshot]` map keyed by paragraph index. This enables the
  application to remember block-level formatting choices independently of inline styling.
- `DocumentController.record_paragraph_style()` stores or updates entries in this map. Consumers fetch copies using
  `DocumentController.paragraph_style()` or `export_paragraph_styles()` when preparing to serialise documents.
- Persistence is intentionally shallow today: metadata lives in memory only. The next milestone for this backlog item is teaching
  `FileService` to emit and read paragraph style payloads (e.g., embedding RTF paragraph control words or DOCX paragraph properties).

## Editing Summaries

- **`EditingController`** derives live metrics (`EditingSummary`) and find/replace results (`ReplacementSummary`). These immutable
  dataclasses provide character, word, and line counts plus replacement statistics. Controllers never touch Tk directly, which
  allows deterministic unit testing.

## Persistence Strategy

- **`FileService`** is the only component performing filesystem IO. It supports three formats today:
  - `.txt` – stored as UTF-8 plaintext.
  - `.rtf` – encoded/decoded using lightweight helpers (`_encode_rtf`/`_decode_rtf`) that handle control words relevant to the
    editor's formatting range.
  - `.docx` – relies on the optional `python-docx` dependency. When absent, attempts raise `RuntimeError` so the GUI can surface a
    clear installation hint.
- Controllers defer to `FileService.read()`/`write()` and simply decide which destination to use. New formats should keep this
  division of responsibility by expanding `FileService` while leaving `DocumentController` untouched.
- Persistence currently stores textual content only. Styling metadata exists exclusively in memory. Future work to round-trip
  formatting should extend `FileService` to emit/consume richer structures (e.g., RTF with styling tags or DOCX runs) and augment
  `DocumentController.snapshot()` once introduced.

## Extending the Model

1. Add or adjust dataclass fields in the relevant controller to capture new state.
2. Update unit tests under `tests/` to cover the expanded behaviour.
3. Document the change here and, if persistence is affected, describe the new format support and migration considerations.

Keeping this document current ensures external contributors can reason about how on-disk artefacts relate to the in-memory editing
model without combing through source files.
