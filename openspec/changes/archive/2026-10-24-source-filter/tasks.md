# Tasks

## 1. Source labels

- [x] 1.1 Add a source registry whose rows are stored id `cli` / argument `cursor-cli` / filter label `Cursor-CLI` / column `Cu-CLI`, then `ide` / `cursor-ide` / `Cursor-IDE` / `Cu-IDE`. Point the column label at that registry and set the source column width to 6. Verify catalog tests that an agent chat's label is `Cu-CLI` and an IDE transcript's label is `Cu-IDE`, and that stored ids stay `cli` and `ide`.

## 2. Picker filter

- [x] 2.1 Show the source line under the workspace header and before the first rule, and render `Cu-CLI` and `Cu-IDE` in the six-character column. Move the column test's first data row down by one line. Verify that workspace, source, and time still share column starts, that `Last updated` still ends the header, and that the wide-workspace cell is still the 24-character capped cell.
- [x] 2.2 Cycle `s` and `S` through All sources, Cursor-CLI, and Cursor-IDE, reset the selection to the first visible row, and apply that filter together with This workspace. Name `s` on the movement line. On the file-name line, `s` appends to the draft and leaves the filter unchanged. Enter on an empty filtered list writes nothing. Verify picker tests for one cycle step, the return to All sources, a workspace change that keeps the source, a typed `s`, the empty Enter, and that the footer still contains `i id` and `Enter names the file`.

## 3. Command line

- [x] 3.1 Accept repeatable `--source` with the registry choices. An unknown value fails before the catalog is read and writes no file. The flag sets the filter the picker opens on, and `s` still advances it. An id outside the filter is reported as not found and writes no file. Passing both current values includes agent chats and IDE transcripts. Verify an export test for `--source cursor-cli`, for `--source other` with no `Chat not found` and no file, for an agent chat id with `--source cursor-ide`, and for a picker that opens on Cursor-CLI and moves to Cursor-IDE on `s`.
- [x] 3.2 Document the source line, `s`, and `--source` in the README. Verify the README contains `Cursor-CLI`, `Cu-CLI`, and `--source`, still contains `Enter asks for a file name.` and `HTML is the default.`, and does not contain `writes nothing`. Verify help contains `cursor-cli` and `cursor-ide`.

## 4. Integration

- [x] 4.1 Run `python -m unittest discover` and verify the suite passes.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
