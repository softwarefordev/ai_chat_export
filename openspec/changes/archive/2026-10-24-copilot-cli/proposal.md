# Proposal

## Why

The exporter lists Cursor agent chats and IDE transcripts, and Copilot CLI sessions sit in a separate local store that it does not read. Those sessions should join the same list and the same HTML or Markdown export.

## What Changes

- Add a registry row for Copilot CLI: stored id `cp-cli`, `--source copilot-cli`, filter label `Copilot-CLI`, column `Cp-CLI`.
- Read `~/.copilot/session-store.db` into the combined newest-first list. `--copilot-root` replaces that default. A missing root adds no rows and does not fail the command.
- Keep a Copilot row when its id also exists as a Cursor session. Title from the summary, then the first user line, then the id. Time from the session's updated timestamp. Workspace from the working directory's last segment.
- Export the turn text by default. `--tools` adds captions from the event log and omits tool results. `--verbose` adds system text, reasoning, and tool results. Leave encrypted content and checkpoint indexes unread.
- Extend the source line and the `s` cycle with Copilot-CLI. Passing only the two Cursor `--source` values is a subset, so the line marks those two and the next `s` returns to All sources.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The catalog, picker, and export include Copilot CLI sessions, and the source filter names that source.

## Impact

- Catalog merge, a Copilot reader, the source registry, picker cycle, and `--copilot-root`. README, help, and tests change.
- HTML and Markdown stay on the existing path. The source cell stays off the written page. VS Code Copilot Chat stays out of this change.
