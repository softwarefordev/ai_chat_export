# Design

## Context

See proposal.md for why. `SESSION_SOURCES` drives the column, the filter line, `--source`, and the `s` cycle. `load_sessions` merges the chat catalog, IDE rows, and Copilot CLI rows, then sorts newest first. `export_session` branches on `chat.source`. `build_transcript` and `caption` already turn user text, assistant text, and tool-call captions into the page. Version-3 JSON and Nitrite documents stay in their own stores. A current VS Code or Rider chat can keep its transcript in `~/.copilot/session-state/<id>/events.jsonl`.

## Goals / Non-Goals

**Goals:**

- One new registry row selects VS Code, Rider, and Visual Studio Copilot sessions together.
- Read those stores read-only with the Python standard library and export them through `build_transcript`.

**Non-Goals:**

- A separate filter or column per IDE host.
- JetBrains AI Assistant chats, and Copilot background-agent databases.
- A general Nitrite or MVStore library, or a Java runtime.
- Showing the source cell on the HTML or Markdown page.
- Rewriting archived change documents or the main spec's title and Purpose.

## Decisions

### One registry row

Append one row after Copilot CLI:

| stored id | `--source` | filter label | column |
| --- | --- | --- | --- |
| `cp-ide` | `copilot-ide` | `Copilot-IDE` | `Cp-IDE` |

`Cp-IDE` is six characters, so `SOURCE_WIDTH` stays 6. The cycle becomes All sources, Cursor-CLI, Cursor-IDE, Copilot-CLI, Copilot-IDE, All sources. `--source` choices come from the registry.

Alternative: three rows (`cp-vsc`, `cp-rd`, `cp-vs`). That names the host in the column and pushes the source line past 80 columns. The chosen filter is one slot and one cell.

### Roots

Add `ai_chat_export/copilot_ide.py`. `load_sessions` gains `vscode_root: Path | None = None` and `copilot_ide_root: Path | None = None`. `None` skips that store. The early return that preserves catalog order applies only when every optional root is `None`. `main` always passes the resolved roots. `export_session` defaults them to `None`, so direct export tests do not scan the user profile.

`--vscode-root` defaults to the stable Visual Studio Code User directory: `%APPDATA%\Code\User` on Windows, `~/Library/Application Support/Code/User` on macOS, and `~/.config/Code/User` on Linux. `--copilot-ide-root` defaults to the local `github-copilot` directory: `%LOCALAPPDATA%\github-copilot` on Windows, `~/Library/Application Support/github-copilot` on macOS, and `~/.config/github-copilot` on Linux. Those non-Windows locations follow the same directory names observed on Windows. A missing root adds no rows.

Do not drop a Copilot IDE id that matches a Cursor id or a Copilot CLI id. Append the IDE rows and sort newest first.

### VS Code documents

List `workspaceStorage/*/chatSessions/*.{json,jsonl}` and `globalStorage/emptyWindowChatSessions/*.{json,jsonl}` under the VS Code root. A JSON document is the session. A JSONL file uses the first snapshot object (`kind` 0, field `v`) and ignores later mutation lines. Skip a session whose requests have no user text and no assistant text.

Title is `customTitle` when it has text, otherwise the first line of the first `message.text`, otherwise the id. Time is `lastMessageDate`, otherwise `creationDate`, as epoch milliseconds, shown with the catalog's local time form. The workspace path is the `folder` file URI in the sibling `workspace.json`; the column is its last segment. An empty-window session has no `workspace.json`, so the column is empty and This workspace omits the row.

`message.text` is the user query. Response parts that carry a `value` string are assistant text. `toolInvocationSerialized` becomes a tool call. Ignore `textEditGroup`, `codeblockUri`, `inlineReference`, `mcpServersStarting`, `undoStop`, `progressTaskSerialized`, and `confirmation`. Drop avatar and icon addresses before rendering.

### Rider and Visual Studio documents

Rider sessions are `rd/chat-agent-sessions/**/copilot-agent-sessions-nitrite.db`. Visual Studio sessions are the same file name under `vs/`. `rd/bg-agent-sessions` stays out of the list. A missing `vs` directory adds no Visual Studio rows.

The file header is MVStore (`H:2,bloc`) and the documents are Java serialization. Read the file with `Path.read_bytes()`. Scan `TC_STRING` values (`0x74` plus a 16-bit length). Do not open the file for write. Two document shapes are sessions. The first groups `sessionId`, timestamps, `source`, and `value`: a `source` of `user` is the user message and a `source` of `copilot` is assistant text, the title is the first user value's first line otherwise the id, the time is `modifiedAt` otherwise `createdAt`, and the workspace column is the last segment of `worktreeState.dirName` or `path`. The second groups `name`, `value`, the following text, `source` plus `copilot`, and `conversationId` plus a UUID. When that UUID has an event log, the log is the transcript and the row is one `Cp-IDE` entry.

Alternative: shell out to Java or add a Nitrite package. The project stays on the standard library, so the scanner is limited to the fields above.

### Event logs

`globalStorage/agent-host.db` is a read-only SQLite file. A `chats_v2` row with `provider_data.sdkSessionId` points at `session-state/<id>/events.jsonl` under the Copilot CLI root. `metadata.data.summary` is the title when it has text. A `tombstoned` row stays out of the list. A missing database adds no rows.

After the IDE rows are merged, any other event log with a user or assistant message whose id is not already listed becomes one `Cp-CLI` row. The title is the first user line. The time is the last event timestamp, shown in the catalog's local time form. The workspace column is the last segment of `session.start` `context.cwd`. An id claimed by a VS Code agent-host link or a Rider conversation id is not also listed as that unlisted row.

A directory path exports through the existing Copilot event reader. The event log and the Nitrite file stay byte-for-byte unchanged.

### Tool captions

Map a Copilot IDE tool id onto the names `caption` already knows, then call `caption`:

| tool id | caption name | argument |
| --- | --- | --- |
| `copilot_readFile` | `Read` | path |
| `copilot_createFile` | `Create` | path |
| `copilot_findFiles` | `Glob` | pattern as `glob_pattern` |
| `run_in_terminal` | `Shell` | description only |
| `copilot_replaceString`, `copilot_multiReplaceString` | `Edit` | path |

Add an `Edit` arm beside `Create`. Any other tool id is its own caption, without argument values. `--tools` shows the caption and omits the result and the command text. `--verbose` adds the result text and still omits the command text.

### Tests and docs

Every `main` path that reaches the catalog passes `--vscode-root` and `--copilot-ide-root` to directories that are not the user's VS Code or `github-copilot` folders. Fixtures are temporary JSON, JSONL, and byte-built Nitrite files. Fixture text must not contain `http`. The page omits `Cp-IDE`.

Update the picker cycle test so the return to All sources is the step after Copilot-IDE. The both-Cursor-flags test omits a Copilot IDE row as well as a Copilot CLI row.

README opening, picker, and closing lines name Cursor and Copilot, including `Copilot-IDE`, `Cp-IDE`, and `copilot-ide`. `pyproject.toml` description and `.github/copilot-instructions.md` name both products. Help lists `copilot-ide`. Leave `Enter asks for a file name.` and `HTML is the default.` in the README.

## Risks / Trade-offs

- [The Nitrite scanner depends on Java string order] → Tests build the `TC_STRING` sequence the reader expects, including `name`, `value`, `source`, `copilot`, and `conversationId`. A future Copilot build that moves fields without those names will warn and omit that file.
- [A current IDE chat can live only in an event log] → The agent-host link or the Rider conversation id claims it as `Cp-IDE`. A log with neither link still appears as `Cp-CLI`.
- [Visual Studio's `vs` layout is inferred from `rd`, and this machine has no IDE hive] → Search for the same chat database name under `vs`. A missing directory adds no rows.
- [JSONL mutation lines can hold draft input] → The transcript comes from the snapshot. Empty snapshots stay out of the list.
- [The source line is wider by `Copilot-IDE`] → Leave it one unwrapped line. At 80 columns the five names still fit.
- [Reading Nitrite by opening it in a Java store would write the file] → `Path.read_bytes()` avoids that. The byte check covers the session file.

## Migration Plan

No stored data moves. Revert the change to drop the registry row, the reader, and the two root flags. The cycle returns to Copilot-CLI and then All sources.
