# Proposal

## Why

The combined list shows which store a session came from, and it cannot be narrowed to one store. A source filter in the picker and on the command line makes that possible, and a later store can join the same filter.

## What Changes

- Add a source line under the workspace scope. `s` cycles All sources, Cursor-CLI, and Cursor-IDE. Left and right still switch All chats and This workspace, and both filters apply together.
- Change the source column from `CLI` and `IDE` to `Cu-CLI` and `Cu-IDE`, six characters wide.
- Add repeatable `--source`, accepting `cursor-cli` and `cursor-ide`. The flag sets the filter the picker opens on, and `s` can still move off it. An id outside the filter is not found. An unknown value is rejected before the catalog is read.
- Keep the source names in one registry so a later store adds a filter label, a column label, and a `--source` value together.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The picker and `--id` can limit the catalog to one or more session sources, and the source column uses the short Cursor labels.

## Impact

- Picker header, footer, column width, and the `s` key. The command gains `--source`. README and the picker column tests change.
- HTML and Markdown output stay as they are. The source cell stays off the written page.
