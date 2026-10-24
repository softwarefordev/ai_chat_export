# Design

## Context

See proposal.md for why. `SESSION_SOURCES` is the registry the column, the filter line, `--source`, and the `s` cycle already read. `load_sessions` merges the chat catalog with IDE rows, drops an IDE id that is already a chat id, and sorts newest first. `projects_root is None` skips IDE rows. `export_session` branches on `chat.source`. `build_transcript` already turns user text, assistant text, `tool-call` captions, `reasoning` parts, system messages, and verbose `tool-result` parts into the page. `caption` knows `Read`, `Glob`, and `Shell`.

## Goals / Non-Goals

**Goals:**

- One new registry row drives the Copilot column, filter label, `--source` value, and the next `s` step.
- Read the Copilot index read-only and export it through `build_transcript`.

**Non-Goals:**

- VS Code Copilot Chat (`chatSessions` and the extension transcript folder).
- Renaming stored ids `cli` and `ide`.
- Showing the source cell on the HTML or Markdown page.
- Decrypting `encryptedContent` or reading `reasoningOpaque`.

## Decisions

### Registry row

Append one row after the IDE row:

| stored id | `--source` | filter label | column |
| --- | --- | --- | --- |
| `cp-cli` | `copilot-cli` | `Copilot-CLI` | `Cp-CLI` |

`Cp-CLI` is six characters, so `SOURCE_WIDTH` stays 6. The cycle becomes All sources, Cursor-CLI, Cursor-IDE, Copilot-CLI, All sources. `--source` choices come from the registry, so `copilot-cli` is accepted without a separate choice list.

Alternative: stored id `copilot`. A later VS Code row would then need a name that does not sound like the whole product. `cp-cli` leaves that name free.

### Catalog from the database, detail from the event log

Add `ai_chat_export/copilot.py`. `load_sessions` gains `copilot_root: Path | None = None`. `None` skips Copilot, matching `projects_root`. `main` always passes the resolved root, default `~/.copilot`, overridable with `--copilot-root`.

Open `<copilot-root>/session-store.db` with a read-only SQLite URI. List `sessions` (`id`, `cwd`, `summary`, `updated_at`). Ignore `session-state` directories that have no session row. Do not drop a Copilot id that matches a Cursor id; the IDE-versus-chat dedupe stays as it is, and Copilot rows are appended before the newest-first sort.

Title is `summary` when it has text, otherwise the first line of the first turn's `user_message`, otherwise the id. `updated_at` is parsed as UTC (`YYYY-MM-DDTHH:MM:SS.sssZ`) into `updated_at_ms` and shown with `format_datetime`. An unparsed value is whitespace-collapsed and used as the row's time label, with `updated_at_ms` of 0 so it sorts last. The workspace column is the last segment of `cwd`. An empty `cwd` leaves the column empty and `filter_workspace` omits the row. A missing root adds no rows. An unreadable database warns `Unreadable Copilot store: {error}` and leaves the other sessions in the list.

Alternative: title and transcript only from `events.jsonl`. The database already has the summary, cwd, and updated time, and on the sessions inspected the summary equals the first user message and the non-empty assistant event text matches `assistant_response`.

### Transcript adapter

`export_session` loads a `cp-cli` chat from `session-state/<id>/events.jsonl` when that file can be read. Walk it in order and emit the message shape `build_transcript` already accepts:

- `user.message` `content` becomes a user text part. Plain text is the query. Ignore `transformedContent`.
- A non-empty `assistant.message` `content` becomes assistant text. Empty assistant events add no text.
- `reasoningText` becomes a `reasoning` part on that assistant message. `encryptedContent` and `reasoningOpaque` are dropped.
- `system.message` becomes a system message, which the transcript shows only for `--verbose`.
- `tool.execution_start` becomes a `tool-call` mapped onto the existing captions: `view` plus `path` is `Read`; `glob` plus `pattern` is `Glob` with `glob_pattern`; `powershell` plus `description` is `Shell`. `grep` plus `pattern` and `create` plus `path` need two caption arms, `Grep` and `Create`. A missing description, path, or pattern uses the same fallback the current caption uses for a missing Shell description.
- `tool.execution_complete` `result` becomes a following `tool` message with a `tool-result` part. `build_transcript` shows that only for `--verbose`. `--tools` therefore captions the call and omits the result.

`checkpoints/index.md` is not read. Other event types are ignored and are not footer lines.

When the event log is missing, build the same user and assistant text from `turns` ordered by `turn_index`. `--tools` then has no captions. When the log exists but cannot be read, warn `Unreadable Copilot events {id}: {error}` and use that turn fallback. A session with no user text and no assistant text uses the existing `Chat has no transcript: {id}` path and writes no file. An empty assistant reply emits no assistant text, so that turn has no Agent heading.

Alternative: always export the `turns` columns and attach tools beside them. The event log is what places each tool inside the stretch, and its non-empty assistant text matched the turn text on the sessions inspected.

### Tests stay off the real store

`export_session` defaults `copilot_root` to `None`, so direct export tests do not open `~/.copilot`. Every `main` path that reaches the catalog passes `--copilot-root` to a directory that is not the user's store. Copilot tests build a temporary root with a small database, an event log, and a checkpoint index. Fixture text must not contain `http`, because the HTML page test rejects that substring. The page still omits `Cp-CLI`, so the existing assertion that the page does not contain `CLI` stays valid.

The picker cycle test that treats the third `s` as a return to All sources moves that return to the fourth step. The both-flags test that expects All sources for `--source cursor-cli --source cursor-ide` expects those two names marked, Copilot omitted, and the next `s` on All sources.

## Risks / Trade-offs

- [Grep argument keys differ between calls (`path` and `paths`)] → The caption reads `pattern` and does not depend on the path key.
- [The source line is wider by `Copilot-CLI`] → Leave it one unwrapped line. At 80 columns the four names still fit. A narrower terminal can clip it, which is the same rule the line already follows.
- [A future column label longer than six characters truncates] → `Cp-CLI` fits. Widening stays a later change.
- [Event assistant text and `assistant_response` could diverge on another install] → When the log is readable, the page uses the log so tools stay in order. The turn table is the fallback.
- [Opening the database writable would touch the WAL] → The read-only URI avoids that. The byte check covers the database, the event log, and the checkpoint index.

## Migration Plan

No stored data moves. Revert the change to drop the registry row, the reader, and `--copilot-root`. Cursor rows and the two-source cycle return.
