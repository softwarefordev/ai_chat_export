# Design

## Context

See proposal.md for why. The transcript builder treats a user text part as the typed prompt when it contains a `prompt_history.json` entry. In current chats that part is a wrapper: a `timestamp` element plus a `user_query` element whose inner text is the prompt. A sibling part holds injected text, and when a Cursor command is present that sibling contains a `cursor_commands` element. `--verbose` currently prints the whole sibling as a context block. Assistant messages have no timestamp. The catalog already formats instants as `Oct 23, 2026 11:13 AM` via `format_datetime`. The chat header uses the chat's `updatedAtMs`.

The main `session-export` spec is still only the unarchived delta in `export-agent-sessions`. This change's delta modifies those requirements.

## Goals / Non-Goals

**Goals:**

- Default You text is the query inner text.
- `--detail` adds the command-block inner text to that You section, once.
- Each visible You and Agent section carries the opening turn's formatted time in both HTML and Markdown.

**Non-Goals:**

- Showing the rest of the injected preamble under `--detail`. That stays on `--verbose`.
- Inventing a time for an Agent section that has no opening user timestamp.
- Changing the picker, themes, tool captions, or the read-only store.

## Decisions

### Query and command are element inner text

Take the inner text of each `user_query` element as the query, and of each `cursor_commands` element as the detail. The surrounding text is not an XML document, so use a small standard-library scan for those two tags rather than an XML parser. If a typed part has no `user_query` element, keep today's fallback: that typed text is the query. Trim surrounding whitespace.

Alternative: treat the whole typed part as the query and strip tags with a generic markup strip. That would still leave command scaffolding when the command sits in the same part, and it would drop the distinction `--detail` needs.

### `--detail` is independent of `--verbose`

`--detail` is a store-false-by-default flag. It does not imply `--verbose` or `--tools`, and `--verbose` does not imply it. When both are set, remove the `cursor_commands` element from the injected context before rendering that context, so the command appears only in the You section.

Alternative: fold command blocks into `--verbose`. The request asks for a separate flag, and verbose already means the raw layers.

### Turn time comes from the user `timestamp` element

Parse `Friday, Oct 23, 2026, 11:13 AM (UTC-7)` into a datetime and format it with the existing catalog helper, dropping the weekday and timezone offset so the line matches the header style. If the text does not match that pattern, collapse whitespace and show it as stored. Copy that formatted string onto the Agent stretch opened by the user turn. A stretch with no opening timestamp has an empty time. The header still uses `updatedAtMs`.

Assistant blobs were checked for time fields; the only time-like values are tool-execution durations, not turn times. Using the opening user timestamp is the time the store actually records for that stretch.

### The time lives on the block

Add an optional timestamp on the transcript block. HTML prints it beside the You and Agent headings. Markdown prints the same string on the heading line. Context, system, and other non-You, non-Agent blocks do not get a turn time.

## Risks / Trade-offs

- [Default exports that previously included the wrapper tags now show only the query] → Called out as breaking in the proposal. Update the transcript tests that assert the full typed part.
- [A future client stores the timestamp in another shape] → Unparsed text is shown as stored, so the turn still has a time.
- [Command text inside injected context is duplicated when both flags are on] → Strip that element from the context block before render.
- [Archiving this change before `export-agent-sessions` has no base spec to modify] → Archive `export-agent-sessions` first.

## Migration Plan

No data migration. After implementation, existing default exports change content as specified. Rollback is reverting the transcript filter and the `--detail` flag.

## Open Questions

None.
