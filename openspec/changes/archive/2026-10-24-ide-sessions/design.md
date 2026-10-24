# Design

## Context

See proposal.md for why. The CLI already lists `~/.cursor/chats/<workspace-hash>/<chat-id>/` and exports `store.db` through `build_transcript`. An IDE session is a different file:

```
<projects-root>/<project-key>/
    .workspace-trusted                         workspacePath
    agent-transcripts/<id>/<id>.jsonl
```

A JSONL line is a `user` or `assistant` object whose `message.content` is a list of `text` and `tool_use` parts, or a `turn_ended` object. `tool_use` carries `name` and `input`. User text still wraps the query in `user_query` and the time in `timestamp`. The file has no tool results and no reasoning parts. `compaction/` beside some transcripts is a summary, not the session.

`build_transcript` already accepts role messages. Assistant captions come from parts of type `tool-call` with `toolName` and `args`. `caption` uses `path` for Read, `glob_pattern` for Glob, and `description` for Shell.

## Goals / Non-Goals

**Goals:**

- Merge both catalogs into one newest-first list and render a three-character source column.
- Adapt a JSONL file into the message list `build_transcript` already accepts.
- Keep tests on synthetic trees via `--projects-root`.

**Non-Goals:**

- Reading `compaction/` or any file that is not `<id>/<id>.jsonl`.
- Decrypting, writing either store, or calling Cursor.
- A separate picker or a fourth scope.
- Putting the source cell into the HTML page or the Markdown file.
- Inventing tool results the JSONL does not contain.
- Changing themes, the navigator, or the turn filter.
- Rewriting unrelated main-spec text that this change does not touch.

## Decisions

### One `Chat` with a source

Add `source` to `Chat`, `"cli"` or `"ide"`, defaulting to `"cli"` so existing constructors stay valid. The picker prints `CLI` or `IDE`. `path` stays the directory that holds the conversation: the chat directory, or the `<id>` directory that contains `<id>.jsonl`.

Alternative: a second row type. The picker, name line, and export already take a `Chat`, so a field keeps one list.

### Merge, then drop shared ids

Load the chat catalog as it works today. Load IDE rows from `--projects-root`, default `~/.cursor/projects`. Drop an IDE row whose id is already in the chat catalog, then sort the combined list by `(updated_at_ms, id)` descending, which is the chat catalog's order. A missing projects root yields no IDE rows and no error, the same as a missing chats root.

Alternative: list both copies. The chat store is the fuller transcript, and the spec says the shared id appears once as `CLI`.

### Title from the first query, time from mtime

Scan the JSONL only until the first user query. The title is that query's first line, or the id when the line is empty. The row time is `int(st_mtime * 1000)`, formatted with the existing catalog stamp. The export still reads the whole file, and turn times inside the page still come from `timestamp` tags.

Alternative: use the last `timestamp` tag as the list time. That reads every line of a multi-megabyte transcript during the catalog scan.

### Workspace from `.workspace-trusted`

Read `workspacePath` from `<project-key>/.workspace-trusted`. The column shows that path's last segment, and This workspace compares the full path the way it already compares a chat's `cwd`. A missing, unreadable, or non-string path leaves `cwd` empty and uses the project folder name. Empty `cwd` already fails the workspace comparison, so the row stays under All chats.

### Adapt lines, then call the existing builder

Each `user` or `assistant` line becomes one message. `text` parts stay `text`. A `tool_use` part becomes `tool-call` with `toolName` set from `name` and `args` set from `input`, so the existing captions apply. The prompts list passed into `build_transcript` is the inner `user_query` strings, which is what marks the typed part today. `turn_ended` is skipped and is not a footer line. Any other line, including a line that is not JSON, is skipped as `line N` (1-based). The existing footer text is `Skipped unrecognized data line N`.

`export_session` loads the combined catalog. A `cli` row still opens `store.db` read-only and still reads `prompt_history.json`. An `ide` row reads `<id>.jsonl` and takes prompts from the query strings above. An empty message list keeps the current "Chat has no transcript" failure.

Alternative: teach `build_transcript` about JSONL. The builder stays store-agnostic, and the adapter is the only new parse.

### Source column in the width math

`SOURCE_WIDTH` is 3. Column order is title, workspace, source, time, with two spaces between columns. The title width loses those three characters and one gap. The header still ends with `Last updated` right-aligned in the 21-character time column and has no source heading. The wide-workspace test currently slices the workspace cell as the 24 characters immediately before the time gap. That slice moves left by `SOURCE_WIDTH + 2`.

### Tests never open the real projects tree

`--projects-root` points at a temporary directory. Fixtures write `.workspace-trusted` and one JSONL. They do not read `~/.cursor/projects`.

## Risks / Trade-offs

- [The JSONL layout is undocumented and can change] → Read only the path above, warn with the id and omit a file that cannot be opened, and keep the fixture shape in tests.
- [A shared id prefers the chat even when the JSONL is newer] → Specified. The chat store carries tool results, reasoning, and the checkpoint history the JSONL does not.
- [`--verbose` on an IDE-only session has no raw tool output] → Do not invent any. Captions still appear when `--tools` or `--verbose` is set.
- [A large transcript is opened twice, once for the title and once for export] → The title scan stops at the first user query.
- [Picker tests assume the workspace cell sits against the time column] → Update that slice in the same change. The `Last updated` header assertion stays valid.
- [The README sentence about aligned columns is asserted exactly] → Update the sentence and the assertion together.

## Migration Plan

No stored data moves. Revert the change to restore a chats-only list.
