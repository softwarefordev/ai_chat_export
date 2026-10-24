# Proposal

## Why

The file-name line marks the insertion point with a static `_`. The terminal's own cursor is left on the line below, so the eye is not drawn to where typing goes.

## What Changes

- While the file name is being edited, the terminal cursor sits in the cell after the visible draft and is a blinking block.
- The draft text no longer includes a `_` character.
- A long draft still shows its end, and one column stays free so the block remains on the name line.
- The chat list hides the cursor. Leaving the picker restores the terminal's normal cursor shape and shows it again, including after Esc and Ctrl+C.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The name line uses the terminal's blinking block cursor at the end of the visible draft.

## Impact

- `ai_chat_export/picker.py` stops appending `_` and reports where the cursor belongs.
- `ai_chat_export/__main__.py` places and shapes the cursor after each frame, and restores it when the picker exits.
- `tests/test_picker.py` frames that expect `file: ..._`.
