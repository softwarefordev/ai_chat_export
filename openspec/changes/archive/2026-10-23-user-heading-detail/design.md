# Design

## Context

See proposal.md for why. The renderers map the user block to the heading You. `query_text` uses `user_query` inner text when that element exists, and otherwise returns the whole typed part. A continuation message that is only a `conversation_summary`, and the opening preamble of `user_info` and rules, have no `user_query`, so they become the user section. `--detail` currently collects only `cursor_commands`. `--verbose` prints the other user parts as a Context section.

The requirements being modified live in the unarchived `user-turn-detail` delta. `openspec/specs/session-export/spec.md` does not exist yet.

## Goals / Non-Goals

**Goals:**

- Visible user headings say User in HTML and Markdown.
- A default user section is the query. Plain typed text with no tags remains a query.
- `--detail` adds the summary and the command block, once, after the query. A summary-only message appears only then.

**Non-Goals:**

- A new flag. Rules, skills, and `user_info` stay on `--verbose`.
- Renaming the agent heading, or changing timestamps, themes, or the read-only store.

## Decisions

### Change the heading text, not the block kind

The HTML and Markdown heading maps use User for the user block. The block kind stays `you`, so the existing section class does not move. Tests that look for the visible heading update from You to User.

### A wrapper-only part is not a query

Take `user_query` inner text when that element is present. Otherwise, if the typed text contains no elements, that text is the query. Otherwise the query is empty. A message with an empty query and no `--detail` blocks produces no User section and does not split the agent stretch.

Alternative: drop the plain-text fallback. The fixture prompts and older chats have no `user_query` element, and those prompts are the query.

### `--detail` collects two elements

When the flag is set, append the inner text of each `conversation_summary` and each `cursor_commands`, after the query, in that order. A summary-only message becomes a User section of that summary text. When `--verbose` is also set, strip both elements from the context block before rendering it.

## Risks / Trade-offs

- [Exports that showed a summary or preamble as the user turn lose that text] → Called out as breaking. `--detail` restores the summary and the command block. `--verbose` still has the preamble.
- [Archiving this change before `user-turn-detail` has no base requirement to modify] → Archive `export-agent-sessions`, then `user-turn-detail`, then this change.

## Migration Plan

No data migration. After implementation, default user sections are the query under a User heading. Rollback is restoring the You heading and the whole-part fallback.

## Open Questions

None.
