# Proposal

## Why

The exporter lists agent chats under `~/.cursor/chats` and leaves out Cursor IDE sessions, which live as JSONL transcripts under `~/.cursor/projects`. Those sessions are the same kind of conversation and should be exportable from the same list.

## What Changes

- Add IDE transcripts to the picker and to `--id`, in one list with agent chats, ordered by last-updated time.
- Show a three-character source column between the workspace and the time: `CLI` for an agent chat, `IDE` for an IDE-only transcript.
- When an id exists in both stores, list it once, from the agent chat, and mark that row `CLI`.
- Read each transcript read-only and run it through the existing HTML and Markdown export. The source cell stays on the picker row.
- Add `--projects-root`, defaulting to `~/.cursor/projects`, so tests can point at a temporary tree.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The catalog includes IDE transcripts, the picker shows which store a row came from, and an IDE id exports through the same transcript path.

## Impact

- Catalog loading, the picker columns, and export-by-id. A new read-only JSONL reader feeds the existing transcript builder.
- README and the picker column tests. HTML themes, the navigator, and the Markdown renderer stay as they are.
- The IDE transcript layout is undocumented and can change with Cursor updates.
