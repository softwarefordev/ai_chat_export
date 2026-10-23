# Proposal

## Why

Re-exporting a chat into the same directory currently stops if the HTML or Markdown file is already there, and it leaves both paths untouched. A presentation loop needs the new export to replace those files.

## What Changes

- **BREAKING**: A successful export replaces an existing HTML file, Markdown file, or both, at the target paths. The command no longer reports a conflict or exits without writing.
- There is no confirmation prompt and no extra flag. Files in the output directory that are not this chat's HTML or Markdown targets stay as they are.
- The chat store stays read-only.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The output-location requirement stops refusing an existing target and replaces those files with the new export. The main spec is not in `openspec/specs/` yet because `export-agent-sessions` is complete and unarchived. Archive that change before this one so the base requirement exists.

## Impact

- `session_export/__main__.py`: drop the existence check that prints `Export already exists` and returns before writing.
- `tests/test_export.py`: the conflict test currently expects no write. It needs to expect replacement.
- `README.md`: the sentence that says an existing target means the command writes nothing.
