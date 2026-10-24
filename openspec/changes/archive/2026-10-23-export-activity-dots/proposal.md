# Proposal

## Why

An export stays quiet until the finished path is printed. A long chat makes that wait look frozen.

## What Changes

- While an export is working and stderr is a terminal, stderr shows a repeating cycle of `...`, `..`, and `.`.
- The cycle covers the quiet work from the start of the export until a path or an error is written, and it is cleared before that message.
- When stderr is not a terminal, the cycle writes nothing. Stdout remains the finished paths.
- Catalog warnings stay on their own stderr lines. The cycle pauses around them.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: An export shows a terminal activity cycle on stderr for the quiet stretch, and stays quiet when stderr is not a terminal.

## Impact

- `ai_chat_export/__main__.py`: run the cycle around the quiet work in `export_session`. The picker and `--id` both use that function.
- `tests/test_export.py`: a terminal stderr records the cycle and a clear line before the path or an error. A non-terminal stderr gains no frames.
