# Tasks

## 1. Columns

- [x] 1.1 Render title, workspace, and time as aligned columns with a fixed 21-character time column, a workspace column capped at 24 from the current page, a flexible title, `...` truncation, a right-aligned Last updated heading, and rules around the rows, and verify a picker test at an explicit width that two titles of different lengths share workspace and time columns, a long title and a long workspace end with `...`, and the existing substrings `> Fantasy Map Maker`, `This workspace *`, and `theme: dark` still match.
- [x] 1.2 Document the three columns in the README, and verify the README says the list shows the title, workspace, and time in aligned columns.

## 2. Selected id

- [x] 2.1 Map `i` and `I` to a toggle that prints `id: ` plus the selected chat id under the footer, hidden on open, updated when the selection moves, and omitted for an empty list, and verify picker tests for hidden, shown, hidden again, a moved selection, and an empty list.
- [x] 2.2 Document the `i` toggle in the README, and verify the README says `i` shows the selected chat id.

## Workflow follow-up

- Archive `export-agent-sessions` before this change so the main picker spec exists before these additions.
- Archive `aligned-picker-columns` after review.
