# Proposal

## Why

The navigator is a 16rem column, and the time shares a row with the prompt. The time wraps, and the prompt that remains is too short to recognize the turn.

## What Changes

- Beside the transcript, the navigator column is 30rem.
- Each entry puts the time on its own line above the prompt. The time is 10px and stays on one line.
- The navigator uses a sans-serif face. The transcript stays in the current serif.
- The prompt still ends with an ellipsis when it does not fit, and it uses the full column width.
- Assumption: the side-by-side layout starts at 70rem, so a 30rem list still leaves room for the transcript. Below that, the list stays a band across the top, with the same stacked rows.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The navigator is a wider stacked list. The time sits above the prompt at 10px.

## Impact

- `session_export/render_html.py`: navigator width, row direction, type size, and face.
- `tests/test_render.py`: the 30rem column, stacked time, 10px time, and sans-serif navigator.
