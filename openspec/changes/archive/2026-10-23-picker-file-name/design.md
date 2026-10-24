# Design

## Context

See proposal.md for why. `run_picker` returns the selected chat id when the user presses Enter, and `export_session` writes immediately. `read_key` drops printable characters. `--name` is passed into both the `--id` path and the picker path.

## Goals / Non-Goals

**Goals:**

- The picker writes only after the file-name line is confirmed.
- `--name` is rejected before the picker opens when no chat id was passed.

**Non-Goals:**

- Letting the picker name line choose a directory.
- Changing the full-path `--name` behavior of an `--id` export.
- Writing a second file from the picker.

## Decisions

### The name line is a second mode of the same picker

After Enter on a chat, `run_picker` stays open and edits a line that starts as the title file name. The extension is `.md` when the caller passes Markdown, and `.html` otherwise. Typing appends. Backspace deletes the last character. Enter confirms. A blank line uses the starting name. Esc returns to the chat list and keeps the selection.

`PickerResult` carries the confirmed file name. The caller writes `out_dir / file_name` and does not pass the CLI `--name` path into that export.

Alternative: a separate prompt after `run_picker` returns. Keeping the line in the picker lets Esc return to the list with the same key stream the tests already inject.

### The confirmed value stays a file name

Separators and the characters the title sanitizer removes are turned into spaces, then collapsed. If the result has no `.html` or `.md` suffix, the export extension is added. The 80-character cap applies to the stem, and the extension is kept. The file is created in `--out` or the current directory.

Alternative: accept a full path on the name line. The request is a file name, with the title-named file as the default.

### Printable keys are returned and ignored on the list

`read_key` returns a printable character instead of dropping it. The chat list still ignores every character except the keys it already handles. The name line is what consumes those characters.

### `--name` without `--id` fails first

`main` checks that case before the picker and before the `--name`/`--out` conflict. The error is printed and the function returns 1. An `--id` export keeps the current full-path `--name` behavior, including the conflict with `--out`.

## Risks / Trade-offs

- [Picker tests and users press Enter once] → Enter now opens the name line. A second Enter accepts the title file name. Update the picker export tests.
- [The list footer still says Enter exports] → Change that footer to say Enter names the file.
- [`output-file-path` still describes `--name` on the picker] → Archive and sync that change first. This change replaces that picker path.

## Migration Plan

No store migration. An `--id --name` command stays valid. A picker command that also passed `--name` now exits with an error. Accepting the picker’s default name writes the same title file as before.
