# Technical Reference

This reference drills into the controllers and services that currently power WordImperfect. It is intended for engineers who need to extend the codebase without reading every module from scratch. Update it whenever controller APIs or service contracts change.

## Controllers

### `DocumentController`

- **Location:** `wordimperfect.controllers.document_controller.DocumentController`
- **Responsibilities:**
  - Tracks the active document path, dirty flag, and paragraph-level styles inside a `DocumentMetadata` dataclass.
  - Delegates all filesystem work to `FileService`, remaining agnostic of concrete encodings.
  - Converts raw JSON payloads returned by the service into typed `ParagraphStyleSnapshot` records so the GUI can rehydrate formatting choices.
- **Key methods:**
  - `open_document(path: Path) -> str` loads text plus paragraph styles; callers should immediately push styles into `TextStyler`.
  - `save_document(text: str, path: Path | None = None) -> Path` writes the primary document and JSON sidecar using `FileService.write_with_styles`.
  - `record_paragraph_style(paragraph_index: int, style: ParagraphStyleSnapshot)` updates the metadata cache after `TextStyler` mutates blocks.
- **Extension points:**
  - `_SUPPORTED_FORMATS` drives file-dialog filters. Add new tuples here when the service layer learns a format.
  - The coercion helpers (`_coerce_alignment`, `_coerce_list_type`, `_coerce_indent`) make the controller tolerant to future metadata revisions.

### `FormattingController`

- **Location:** `wordimperfect.controllers.formatting_controller.FormattingController`
- **Responsibilities:**
  - Maintains inline toggles (bold/italic/underline) plus paragraph alignment, indent, list type, and colour/font selections via a mutable `FormattingState`.
  - Supplies snapshots for display (`state`) and for persistence (`paragraph_style`).
- **Key methods:**
  - Toggle helpers (`toggle_bold`, `toggle_italic`, `toggle_underline`) return the updated boolean so toolbar buttons can refresh their pressed state.
  - `set_alignment` accepts either `Alignment` enums or raw strings, enabling menu callbacks to pass Tk variable values directly.
  - `cycle_alignment` implements the toolbar's rotate-through-alignment behaviour without GUI code knowing enum order.
- **Extension points:**
  - Additional inline attributes (e.g., strikethrough, highlight colour) should be added to `FormattingState` and applied in `TextStyler._apply_inline`.

### `TextStyler`

- **Location:** `wordimperfect.controllers.text_styler.TextStyler`
- **Responsibilities:**
  - Bridges `FormattingState` into Tk text widget mutations.
  - Applies inline font configuration, paragraph alignment tags, indent margins, and list prefixes.
- **Key methods:**
  - `apply(state: FormattingState)` orchestrates list, inline, and paragraph updates in that order so list replacements see the latest indent depth.
  - `_apply_list` rewrites selected lines with bullet/number prefixes. It defaults to the insertion line when no selection exists, matching common word processor UX.
  - `_selection_range` and `_line_range_at_insert` normalise Tk index strings to reduce duplication across helpers.
- **Extension points:**
  - Widget interaction remains encapsulated. When adding new styling primitives, mirror them here so controllers stay toolkit-agnostic.

### `EditingController`

- **Location:** `wordimperfect.controllers.editing_controller.EditingController`
- **Responsibilities:**
  - Computes derived metrics (`EditingSummary`) and search results (`SearchMatches`, `ReplacementSummary`) for arbitrary text.
  - Implements case-sensitive/case-insensitive search without binding to Tk widgets, which keeps unit tests straightforward.
- **Key methods:**
  - `summarize(text)` powers the status bar counters.
  - `find_matches` exposes all match offsets; the GUI uses this to highlight matches incrementally.
  - `replace(..., replace_all=False)` supports "replace next" flows by returning both the updated text and the index of the substituted span.
- **Extension points:**
  - Regex support can slot into `find_matches` by gating on a new flag and returning spans from `re.finditer`.

### `ObjectInsertionController`

- **Location:** `wordimperfect.controllers.object_insertion_controller.ObjectInsertionController`
- **Responsibilities:**
  - Maintains a registry mapping human-readable labels to callables that return embedded objects (images, future OLE-style payloads).
  - Provides Tk menu population data via `available_objects`.
- **Extension points:**
  - Handlers can accept arbitrary parameters; the GUI forwards arguments through `insert` so third-party plugins can prompt for file paths or metadata.

## Services

### `FileService`

- **Location:** `wordimperfect.services.file_service.FileService`
- **Responsibilities:**
  - Implements read/write for `.txt`, `.rtf`, and `.docx` using UTF-8 encoding and optional `python-docx` integration.
  - Persists paragraph styles to a `*.styles.json` sidecar, insulating controllers from filesystem details.
- **Key methods:**
  - `read(path)` dispatches based on suffix and normalises RTF/Docx into newline-delimited text.
  - `read_with_styles(path)` pairs the textual payload with decoded style metadata, returning an empty mapping when the sidecar is absent.
  - `write_with_styles(path, text, paragraph_styles)` serialises the JSON sidecar (or removes it) after writing the main document.
- **Extension points:**
  - `_encode_rtf`/`_decode_rtf` centralise the minimal RTF subset; expand them when richer formatting (colours, font tables) is required.
  - To embed paragraph styles directly inside `.docx`, swap the JSON serialisation with XML node manipulation before `Document.save()`.

## Module Interaction Flow

1. **User edits text** – Tk events modify the text widget. `TextStyler` listens for toolbar/menu changes and applies the latest `FormattingState` to the selection or current line.
2. **Formatting persistence** – When paragraphs change, the application records snapshots via `DocumentController.record_paragraph_style`. These snapshots feed the JSON metadata persisted by `FileService`.
3. **Find & replace** – Dialog interactions call `EditingController.find_matches`/`replace`. The GUI highlights spans returned from `SearchMatches.spans()` and issues incremental replacements without reimplementing search mechanics.
4. **Saving** – `DocumentController.save_document` exports both text and paragraph metadata through `FileService.write_with_styles`, ensuring formatting survives editor restarts even for plaintext formats.

## Testing Considerations

- Controllers are pure Python and covered by `tests/test_controllers_logic.py`. Add new assertions there when controller behaviour evolves.
- `TextStyler` relies on a fake widget in tests to validate tag manipulation. New styling paths should extend the fake accordingly so we retain deterministic coverage without a GUI environment.
- When augmenting `FileService`, add regression tests around encoding/decoding paths to prevent format-specific regressions.

Keeping this document aligned with the code makes onboarding easier and provides a single index of extension hooks for future feature work.
