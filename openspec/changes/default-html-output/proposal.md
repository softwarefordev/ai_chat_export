# Proposal

## Why

Every export writes an HTML page and a Markdown file. The page is the presentation. The Markdown copy is extra, and a default run should leave it out.

## What Changes

- **BREAKING**: A default export writes and prints only the HTML file. It does not create a Markdown file, and it leaves an existing Markdown file unchanged.
- New `--markdown` flag also writes the Markdown file beside that HTML page, from the same filtered transcript, and prints both paths.
- A file this export writes is still replaced when it already exists. A file this export does not write is left alone.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The paired-output and output-location requirements write HTML by default and add Markdown only with `--markdown`. The Markdown file, when written, still matches the HTML turns and has no color theme. The main spec is not in `openspec/specs/` yet. Archive `export-agent-sessions`, then `overwrite-existing-output`, before this change. This delta keeps the replace-on-write behavior from `overwrite-existing-output` and changes which files a default export writes.

## Impact

- `session_export/__main__.py`: add `--markdown` and write the Markdown file only when it is set. The picker and `--id` paths both use that flag.
- Tests that expect a Markdown file on a default export, including `tests/test_export.py`, `tests/test_end_to_end.py`, and `tests/test_picker.py`.
- `README.md`: describe HTML as the default and `--markdown` as the extra file.
- The Markdown renderer stays. No new dependencies. The chat store stays read-only.
