# Proposal

## Why

In the middle of the navigator, a turn time sits closer to the prompt above it than to the prompt it belongs to. A reader cannot tell which row the time labels.

## What Changes

- The space between a turn time and the prompt under it becomes smaller than the space between navigator entries.
- The time stays on its own line above that prompt, at the same size, on one line.
- Rows with no turn time keep the same space between entries.
- The first entry keeps its place under the top of the list. Markdown, the checkboxes, and Clear filter stay as they are.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: A navigator turn time groups with the prompt below it, and entries are separated by a larger gap.

## Impact

- `ai_chat_export/render_html.py` changes the navigator spacing.
- `tests/test_render.py` checks that the time sits closer to its prompt than the entries sit to each other.
