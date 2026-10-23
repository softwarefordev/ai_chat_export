# Tasks

## 1. Query portion

- [x] 1.1 Extract each `user_query` element's inner text as the You body, and when that element is absent use the typed prompt text, and verify a transcript unit test includes the inner query and omits timestamp tags and injected context.
- [x] 1.2 Keep Cursor command blocks, tool captions, system text, reasoning, and raw tool output off the default transcript, and verify the default transcript tests still pass without `--detail`, `--tools`, or `--verbose`.

## 2. Detail flag

- [x] 2.1 Add `--detail` and place each `cursor_commands` element's inner text once after the query in that You section, and verify unit tests for a turn with a command, a turn without one, and `--detail` plus `--verbose` where the injected context does not repeat the command.
- [x] 2.2 Document `--detail` in the README and in `--help`, and verify `session-export --help` lists the flag and the README describes what it shows.

## 3. Turn timestamps

- [x] 3.1 Put the catalog-style time from the user turn's `timestamp` element on that You section and on the Agent stretch it opens, show unparsed timestamp text with whitespace collapsed, and omit the time when none is recorded, and verify a transcript unit test turns `Friday, Oct 23, 2026, 11:13 AM (UTC-7)` into `Oct 23, 2026 11:13 AM`.
- [x] 3.2 Render that time on the You and Agent sections in HTML and Markdown while leaving the chat header time in place, and verify render tests for both files.

## 4. Export check

- [x] 4.1 Export a synthetic chat that has a wrapped query, a command block, and a turn timestamp, and verify the written HTML and Markdown match the default query, the `--detail` command text, and the formatted turn time.

## Workflow follow-up

- Archive `export-agent-sessions` before this change so `openspec/specs/session-export/spec.md` exists for the modified requirements.
- Archive `user-turn-detail` after review.
