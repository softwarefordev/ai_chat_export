# Proposal

## Why

`--markdown` writes a Markdown file and an HTML page. A Markdown export should write only the Markdown file.

## What Changes

- **BREAKING**: Passing `--markdown` writes the Markdown file and prints that path. It does not write an HTML file.
- An existing HTML file stays as it is. An existing Markdown file is still replaced.
- A default export still writes only HTML.
- Help text and the README describe `--markdown` as the Markdown export.

The requirements being modified live in the unarchived `default-html-output` delta. Archive `export-agent-sessions`, then `overwrite-existing-output`, then `default-html-output`, before this change, so those requirements are in the main spec.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: `--markdown` writes Markdown only. The default export still writes HTML. Markdown still has no color theme.

## Impact

- `ai_chat_export/__main__.py`: skip the HTML write and the HTML path when `--markdown` is set. The picker and `--id` both use that path.
- `README.md` and `--help`: describe the Markdown-only export.
- `tests/test_export.py`, `tests/test_picker.py`, and `tests/test_end_to_end.py`: expect one file and one printed path.
