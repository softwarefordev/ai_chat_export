# Proposal

## Why

Cursor agent sessions are the record of a live demonstration, but the only way to open one again is the CLI resume picker. Talks and write-ups need a page and a transcript that follow the chat, without pasting the raw session store into a slide.

## What Changes

- Add a CLI that lists local Cursor agent chats in the same shape as `agent ls`: title, workspace name, last updated, `All chats` and `This workspace`, keyboard navigation, Enter to export, Esc to close.
- Export the selected chat to HTML and Markdown from one filtered transcript.
- The default transcript shows the typed prompt and the assistant's visible text. Consecutive assistant messages, up to the next typed prompt, share one Agent heading. Tool captions appear with `--tools` or `--verbose`. System text, injected context, reasoning, and raw tool output are included only with `--verbose`.
- HTML is dark unless the user passes `--theme light`. The theme is chosen when the file is written.
- The picker shows the theme that will be written and does not delete chats.
- The page uses an original stylesheet. It does not ship Cursor's logo, fonts, icons, or CSS.
- The tool depends only on the Python standard library.

## Capabilities

### New Capabilities

- `session-export`: List local agent chats, select one, and write an HTML page and a Markdown transcript of the filtered session.

### Modified Capabilities

- None. The project has no existing specs.

## Impact

- Greenfield repository: a new Python CLI, with no existing application code to modify.
- Read-only use of the local Cursor agent chat store at `~/.cursor/chats` (`schemaVersion` 1). The store layout is undocumented and can change with Cursor updates.
- No new third-party dependencies. The interactive picker uses ANSI input (`msvcrt` on Windows, `termios` elsewhere) because this Windows Python has no `curses`.
- Outputs are files written for the user. The tool does not modify Cursor's data or call Cursor's APIs.
