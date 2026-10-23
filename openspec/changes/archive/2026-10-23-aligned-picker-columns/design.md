# Design

## Context

See proposal.md for why. `render_frame` joins the title, workspace, and time with four spaces, so the time column drifts. The active scope is marked with `*`, the selected row with `>`, and the footer includes `theme: dark` or `theme: light`. `read_key` maps the arrows, Enter, Esc, and Backspace. Any other character, including `i`, is ignored. Existing picker tests look for the substrings `> Fantasy Map Maker`, `This workspace *`, and `theme: dark`.

A catalog stamp uses an unpadded day, so `Sep 1, 2026 09:05 AM` is shorter than `Aug 15, 2026 04:42 PM`.

## Goals / Non-Goals

**Goals:**

- Three aligned columns, with widths computed from the visible page.
- An `i` toggle that prints the selected chat id under the footer.

**Non-Goals:**

- Color, a fourth id column, or a launch flag.
- Changing Enter, Esc, Backspace, or the theme line.

## Decisions

### Fixed time column, capped workspace, flexible title

The time column is 21 characters, the width of `Aug 15, 2026 04:42 PM`. Shorter stamps are right-aligned in that width. `Last updated` is right-aligned in the same width. The workspace column is the longest workspace name on the current page, capped at 24 characters. Two spaces separate the columns. The title receives the remaining width after the `>` marker and those columns. Truncate with `...`, keeping the marker and the time column on the row.

Alternative: pad the workspace to the longest name in the whole catalog. The page would jump less while scrolling, and one long name off-screen would shrink every title. The page width matches what the reader can see.

`render_frame` takes an explicit `width`. When the caller omits it, use the terminal width. Tests pass a width so they do not follow the developer's window.

### Keep the markers the tests already match

The selected row still starts with `> `, and an unselected row starts with two spaces, so the title column is shared. The active scope still uses `*`, including the substring `This workspace *`. The theme line stays. The movement line gains `i id`. A row of `-` matching the frame width sits under the header and above the footer.

### `i` toggles one footer line

`read_key` returns `i` for both `i` and `I` on Windows and POSIX. `run_picker` starts with the id hidden. Each `i` flips that flag and repaints. The line is `id: ` plus the selected chat id, after the theme line. If the visible list is empty, the line is omitted even when the flag is on. Moving the selection updates the line. The id is not placed in a column.

## Risks / Trade-offs

- [A very narrow terminal leaves the title only a few characters] → Truncate the title rather than wrap the row. The time column keeps its width.
- [Archiving this change before `export-agent-sessions` creates a main spec that has only these additions] → Archive `export-agent-sessions` first.

## Migration Plan

No data migration. The next picker open uses the columns. Rollback is the space-separated row.

## Open Questions

None.
