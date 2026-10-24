# Proposal

## Why

User sections are labeled You, and a message that has no query is still printed in full. A continuation summary and the opening preamble then show up as the user turn. The page should label that side User and keep the default to the query.

## What Changes

- **BREAKING**: HTML and Markdown label a user section **User**. The agent section stays **Agent**.
- **BREAKING**: A default user section is only the inner `user_query`. Plain typed text with no wrapper elements stays the query. A message that is only a `conversation_summary`, a `cursor_commands` block, or other injected context does not appear.
- `--detail` adds the conversation summary and the Cursor command block inside that User section. A summary-only message appears only when the flag is on.
- `--verbose` still shows the remaining injected context, including `user_info`, rules, and skills. It does not, by itself, add the summary or the command block to the User section. When both flags are set, each of those blocks appears once.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The default transcript, verbose transcript, user-turn detail, and turn-timestamp requirements use a User heading, omit wrapper-only messages by default, and show `conversation_summary` with the command block under `--detail`. The main spec is not in `openspec/specs/` yet. Archive `export-agent-sessions`, then `user-turn-detail`, before this change.

## Impact

- `session_export/transcript.py`: stop treating a wrapper-only part as the query. Collect `conversation_summary` with the command text when `--detail` is set, and strip both from verbose context so they are not repeated.
- `session_export/render_html.py` and `session_export/render_md.py`: the user heading text becomes User.
- Tests that expect a You heading, and tests that expect unwrapped typed text to remain the query.
- `README.md`: say the user section is labeled User, and that `--detail` includes the summary and command blocks.
- No new flag and no new dependencies. The chat store stays read-only.
