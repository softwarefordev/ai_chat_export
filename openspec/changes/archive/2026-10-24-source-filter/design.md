# Design

## Context

See proposal.md for why. The picker already has two filters' worth of keys: left and right toggle `scope` between `all` and `workspace`, and each row's `source` is `"cli"` or `"ide"`. `source_label` prints `CLI` or `IDE` in a column `SOURCE_WIDTH` of 3, between the workspace and the time. `render_frame` starts with the scope header, then a rule. The movement line names `i` and does not name a source key. `s` on the list is ignored. On the file-name line it is a typed character.

## Goals / Non-Goals

**Goals:**

- One registry of sources drives the column label, the filter label, the `--source` value, and the `s` cycle.
- Apply the source filter and the workspace scope together, in the picker and for `--id`.

**Non-Goals:**

- Renaming the stored `source` values `"cli"` and `"ide"`.
- Putting the source filter on the HTML page or in the Markdown file.
- Changing what left and right do.
- A picker control that builds an arbitrary subset. A subset of more than one source comes from repeating `--source`.

## Decisions

### Registry, stored id unchanged

A small table, in order:

| stored id | `--source` | filter label | column |
| --- | --- | --- | --- |
| `cli` | `cursor-cli` | `Cursor-CLI` | `Cu-CLI` |
| `ide` | `cursor-ide` | `Cursor-IDE` | `Cu-IDE` |

`source_label` returns the column cell. A later store adds one row. The cycle, the flag choices, and the filter line read the table.

Alternative: store `cursor-cli` on `Chat`. Existing catalog tests and the export branch compare `"cli"` and `"ide"`. The public names can change without rewriting those ids.

### Filter state is the allowed set

`None` means every source. A set means those stored ids. The workspace filter runs first, then the source filter. Left and right change only the workspace scope and reset the selection to the first visible row. `s` does the same for the source filter.

The cycle is All sources, then each registry row. From All sources, `s` selects `cli`. From `cli`, `s` selects `ide`. From `ide`, `s` selects All sources. `S` does the same on the list. On the file-name line both characters stay typed input.

A set that is neither All sources nor exactly one registry id has no cycle slot. The next `s` selects All sources, and the cycle continues from there. With the two current sources, repeating both flags is the full set, so the line marks All sources and the first `s` selects Cursor-CLI.

### Source line under the scope header

`render_frame` gains the allowed set and prints one line after the scope header and before the first rule. Four spaces separate the names, matching `All chats *    This workspace`. The active name, or each name in a proper subset, gets ` *`. All sources gets ` *` only when every registered source is allowed. The movement line gains `s source`.

The column test reads the first data row at `lines[2]`. That row moves down by one. `SOURCE_WIDTH` becomes 6. The wide-workspace slice already uses `SOURCE_WIDTH`, so it follows the constant. `Last updated` stays the right end of the header.

### `--source` is repeatable

`argparse` `action="append"` with choices taken from the registry. An unknown value fails in argparse, before `load_sessions`. The accepted values map to stored ids. Export and the picker both see the filtered catalog, so an id of another source is the existing `Chat not found` path. Omitting the flag passes `None`.

Alternative: a single `--source` choice. Repeating the flag is what lets a later third source be excluded while the other two remain.

## Risks / Trade-offs

- [The movement line grows by `s source`] → Keep the existing footer words and append the new key. Tests that match those words still pass.
- [The source line shifts every frame's row numbers] → Update the column test's unpack. The bottom rule stays `lines[-3]` for a two-row frame.
- [A future column label longer than six characters truncates with `...`] → The width stays 6 so `Cu-CLI` and `Cu-IDE` fit exactly. A longer label is a later change to the width, not a second column.
- [HTML tests forbid the substrings `CLI` and `IDE`] → The page still omits the source cell, so those assertions stay valid. Picker and catalog assertions that expect the cell `CLI` move to `Cu-CLI`.

## Migration Plan

No stored data moves. Revert the change to restore the three-character `CLI` and `IDE` cells and a list with no source filter.
