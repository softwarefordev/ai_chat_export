# Proposal

## Why

`--name` currently chooses the file for the list picker as well as for `--id`. The picker should ask for a file name after a chat is selected, and the title-named file should stay the default.

## What Changes

- **BREAKING**: `--name` applies only with `--id`. Passing `--name` without a chat id reports an error, does not open the picker, and writes no file.
- **BREAKING**: Enter on a selected chat opens a file-name line and does not write yet. The line starts as the title file name, or the chat id when there is no title. `--markdown` uses `.md`; otherwise the name uses `.html`.
- Enter on that line writes the export under the confirmed name in `--out` or the current directory. An empty line uses the title file name. Typing appends, and Backspace deletes. Esc on the line returns to the list and writes nothing.
- The confirmed picker name is a file name in the output directory. It is not a full path.
- With `--id`, `--name` stays a full path and still conflicts with `--out`.

The implemented export writes one file. The main spec still says the picker writes HTML and Markdown. This change names the one file the export writes. Accepting the default keeps the title file name.

`output-file-path` is still active and sends `--name` through the picker. Archive and sync that change before this one so its `--id` path rules are in the main spec first. This change replaces the picker half of that behavior.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The picker asks for a file name after selection. `--name` is limited to an export by chat id.

## Impact

- `ai_chat_export/picker.py`: add the name line and return the confirmed file name. `read_key` must yield printable characters for that line.
- `ai_chat_export/__main__.py`: reject `--name` without `--id` before the picker. Stop passing `--name` into the picker export. Write the confirmed picker name in the output directory.
- `README.md`: describe the picker name line and that `--name` requires `--id`.
- `tests/test_picker.py` and `tests/test_export.py`: confirm the default with a second Enter, cover an edited name, and cover `--name` without `--id`.
