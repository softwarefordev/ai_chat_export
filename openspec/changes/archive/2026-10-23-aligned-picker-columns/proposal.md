# Proposal

## Why

The picker prints the title, workspace, and time in one drifting line, so the clock moves with the length of the title. The list should read as three columns, and the selected chat's id should be available without putting it in those columns.

## What Changes

- The picker shows title, workspace, and last-updated time in three aligned columns. A Last updated heading sits on the time column. Rules separate the header and the footer. The selected row stays marked with `>`.
- The time column has a fixed width. The workspace column matches the longest name on the current page, up to a cap. The title uses the remaining width. A value that does not fit ends with `...`.
- Pressing `i` toggles a line under the footer that shows the selected chat's id. It is hidden when the picker opens, follows the selection while visible, and is omitted when the list is empty.
- Backspace still does not delete. The footer still names the theme Enter will write. No new launch flag.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The picker gains aligned columns and a toggle for the selected chat id. The main spec is not in `openspec/specs/` yet. These requirements are additions. Archive `export-agent-sessions` before this change so the rest of the picker spec is already there.

## Impact

- `session_export/picker.py`: column layout, truncation, and the `i` key.
- `tests/test_picker.py`: alignment, truncation, and the id toggle. Tests pass an explicit width so they do not depend on the real terminal.
- `README.md`: mention the columns and the `i` toggle.
- No new dependencies. The chat store stays read-only.
