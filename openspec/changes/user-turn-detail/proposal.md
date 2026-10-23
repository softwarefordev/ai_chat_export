# Proposal

## Why

A user turn in the store wraps the typed prompt in markup and often attaches a Cursor command block plus other injected text. The default export currently prints that whole typed part, so a presentation shows tags and command scaffolding instead of the query. Turns also have no time of their own; only the chat header has a timestamp.

## What Changes

- **BREAKING**: A user turn's default text is only the query portion (the inner text of the `user_query` element). Timestamp tags, command wrappers, and other non-query user text are omitted.
- New `--detail` flag shows the other user-turn detail, starting with Cursor command blocks (the inner text of `cursor_commands`). It does not dump the rest of the injected preamble; that stays on `--verbose`.
- `--verbose` still shows system text, remaining injected context, reasoning, tool captions, and raw tool output. It does not, by itself, add the command block to the You turn. When both flags are set, the command block appears once.
- Every visible You turn and every Agent section shows a formatted local timestamp in the same style as the catalog (`Oct 23, 2026 11:13 AM`). The chat header timestamp stays.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: Default user text becomes the query portion only; `--detail` exposes Cursor command blocks; each visible You and Agent section carries a formatted timestamp. The main spec file is not in `openspec/specs/` yet because `export-agent-sessions` is complete and unarchived. This delta modifies that capability's requirements. Archive `export-agent-sessions` before this change so the base spec exists.

## Impact

- `session_export/transcript.py`: split the query from command blocks and other user text; attach a timestamp to each visible user turn and the agent stretch it opens.
- `session_export/__main__.py`: add `--detail` and pass it through.
- `session_export/render_html.py` and `session_export/render_md.py`: print the per-turn time with the You and Agent headings.
- Tests and README for the default query, `--detail`, and turn timestamps.
- No new dependencies. The store stays read-only.
