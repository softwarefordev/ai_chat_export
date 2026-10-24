# Proposal

## Why

Exports are named from the chat title. A chosen path is needed when that name is not the file the user wants.

## What Changes

- Add `--name`, a full file path with a directory and an extension. That path is the only file written.
- `--name` replaces `--out`. Passing both is an error and writes nothing.
- The path is used as given. The export does not add `.html` or `.md`. The file contents still follow `--markdown`.
- A relative path is relative to the current directory. Missing parent directories are created. An existing file at that path is replaced.
- Omitting `--name` keeps title-or-id naming and `--out`.

The implemented export writes one file. The main spec still says `--markdown` also writes an HTML file. This change leaves that no-name case as specified. One path can name one file, so `--name` with `--markdown` writes Markdown to that path and does not add a second file.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: Output location and names accepts a full output path. Omitting `--name` keeps the current naming rules.

## Impact

- `ai_chat_export/__main__.py`: accept `--name` on the picker path and the `--id` path, write that path, and reject it together with `--out`.
- `README.md` and `--help`: describe `--name`.
- `tests/test_export.py` and `tests/test_picker.py`: cover the named path, replacement, a relative path, and the `--out` conflict.
