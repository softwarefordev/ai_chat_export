# Design

## Context

The package `session_export` already exports a chat to HTML and Markdown. This revision changes two behaviors: consecutive assistant messages share one Agent heading, and tool captions appear only with `--tools` or `--verbose`. See `proposal.md` for why the exporter exists, and `specs/session-export/spec.md` for the behavior the CLI has to meet. Cursor agent chats live on disk under `~/.cursor/chats`.

Observed store, `schemaVersion` 1, from local sessions:

```
~/.cursor/chats/<workspace-hash>/<chat-id>/
    meta.json              title, cwd, createdAtMs, updatedAtMs, hasConversation
    prompt_history.json    list of strings the user typed
    store.db               sqlite: blobs(id, data), meta(key, value)
```

The sqlite `meta` value is hex-encoded JSON. It includes `latestRootBlobId`. The root blob is binary and lists child blob ids as raw 32-byte SHA-256 digests, in conversation order. Message blobs are JSON:

- `role`: `system`, `user`, `assistant`, or `tool`
- `content`: a string, or a list of parts
- part `type`: `text`, `reasoning`, `tool-call`, `tool-result`
- `tool-call` fields used for captions: `toolName`, `args`
- `Read` args include `path`; `Glob` args include `glob_pattern`; `Shell` args include `command` and a short `description`
- `tool-result` carries `result`

In the session that was inspected, the root's direct children were the message JSON blobs in order, followed by one binary blob that pointed at those same messages again. User messages mixed a long injected context part with a shorter typed part. The typed part was the one that contained the matching `prompt_history.json` string. Message bytes were plaintext JSON whose SHA-256 matched the blob id. The sqlite meta also carries a `blobEncryptionKey` field; this design does not decrypt with it.

Windows CPython here has no `_curses` module. The picker has to use ANSI plus `msvcrt` on Windows and `termios` on other platforms.

## Goals / Non-Goals

**Goals:**

- Read the `schemaVersion` 1 store above and produce the filtered transcript in `specs/session-export/spec.md`.
- Keep catalog, transcript, HTML, and Markdown as separate steps so each can be tested with a synthetic fixture.
- Bake one theme into each HTML file.

**Non-Goals:**

- Writing, deleting, or resuming chats.
- Reading IDE transcript JSONL under `~/.cursor/projects`.
- Decrypting blobs, calling Cursor APIs, or depending on the `agent` CLI at runtime.
- Shipping Cursor trademarks, icons, fonts, or stylesheets.
- A browser theme toggle. Theme is fixed when the file is written.
- A general Markdown engine. Assistant text uses a small subset renderer.

## Decisions

### Python package, standard library only

The CLI is a package `session_export` with a `pyproject.toml` script named `session-export` and no third-party dependencies. `python -m session_export` is the same entry. Modules:

- `catalog` reads `meta.json` and `prompt_history.json`
- `store` opens `store.db` read-only and walks the root blob
- `transcript` builds the filtered turns
- `render_html` and `render_md` write the two files
- `picker` draws the list
- `__main__` parses arguments

Alternative considered: one script. A package keeps the store reader testable without the terminal. Alternative considered: Node with no dependencies. Python is the runtime that already has `sqlite3` in the standard library on this machine.

### Catalog from `meta.json`

Walk `~/.cursor/chats/*/*/meta.json`. A chat is `{id, title, cwd, workspace_name, updated_at, has_store}`. `workspace_name` is the last segment of `cwd`. Sort by `updatedAtMs` descending. Compare workspace paths for This workspace with normalized absolute paths, case-insensitive on Windows.

`schemaVersion` other than 1: omit the chat and warn on stderr. Unreadable metadata: omit and warn. A chat whose `meta.json` parses and whose `store.db` is missing stays in the list with `has_store` false.

Timestamp display: local time as `Aug 15, 2026 04:42 PM`.

### Transcript from direct message children

Open `store.db` with a read-only URI. Decode the hex `meta` value, load `latestRootBlobId`, and scan that blob for non-overlapping 32-byte digests that are blob ids. Keep direct children that are JSON objects with a `role`. Do not recurse into a later binary child that only repeats those ids, so the checkpoint blob does not duplicate the transcript.

Typed user text is a `text` part, or string content, that equals or contains a `prompt_history.json` entry. Other user text is injected context. Assistant `text` parts are visible. Assistant `reasoning` parts, `system` content, and `tool-result` payloads are verbose-only.

### One Agent heading per stretch

Walk messages in root-blob order and open an agent stretch at the first assistant or tool message after a typed user prompt. Append later assistant text, captions, reasoning, and tool results to that same stretch. The next typed user prompt closes it. HTML renders one `<h2>Agent</h2>` for the stretch. Markdown renders one `## Agent`. A stretch whose visible body would be empty, because the default export hides tool-only work, produces no heading.

Captions, when shown, stay between the assistant paragraphs from the message that issued the call and the next assistant text. Verbose reasoning and raw tool output stay inside the same heading, next to the captions.

### Tool captions are opt-in

`--tools` adds captions and still omits raw tool output. `--verbose` adds system text, injected context, reasoning, raw tool output, and the captions, so a tool body is not shown without its label. A default export shows neither.

Caption text:

- `Read`: `Read` plus `path`
- `Glob`: `Glob` plus `glob_pattern`
- `Shell`: `Ran` plus `description` when present; otherwise `Ran command`, still without the command string
- any other tool: `toolName` only

Alternative considered: render the JSONL files under `agent-transcripts`. Those files are a thinner log and are not the `agent ls` catalog.

### HTML document

One HTML file, UTF-8, stylesheet in a `<style>` block, no scripts and no external URLs. CSS variables hold the palette. Dark and light each define background, body text, muted labels, timestamp color, user block, agent block, and tool-line marker. The renderer writes exactly one of those palettes.

Layout: title and workspace on the left, timestamp on the right, then a `You` block and one `Agent` block per stretch. A `>` line per tool caption appears inside that Agent block when captions are enabled. Assistant text runs through a small subset renderer: fenced code, indented code, paragraphs, lists, and inline code. The footer lists skipped blobs and unlinked images only when there is something to name. An image part that is actually on a visible turn is embedded as a data URI; an image blob that no visible turn references is footer-only, per the spec.

The palette is original. No Cursor logo, font files, or copied stylesheet.

### Markdown document

The same turns as the HTML file: a title heading, a workspace and timestamp line, `## You`, and one `## Agent` per stretch. Tool captions are list items inside that Agent section when `--tools` or `--verbose` is set. Verbose reasoning and tool output stay under that same `## Agent` heading. No color tokens.

### CLI

```
session-export [--id <chat-id>] [--theme light|dark] [--tools] [--verbose] [--out <dir>]
```

`--theme` defaults to `dark`. `--tools` defaults to off. `--verbose` implies captions plus the raw layers. `--out` defaults to the current directory. File stems are the title sanitized for Windows file names, or the chat id when the title is empty. Extensions are `.html` and `.md`. If either path exists, print the conflict and write nothing.

No chat id: open the picker. The footer shows `theme: dark` or `theme: light`, the selection index, and the key hints for move, scope, Enter, and Esc. Enter exports the row. Esc exits 0 with no files. Backspace does not delete. The list scrolls inside the terminal height. Arrow keys use `msvcrt` on Windows and raw `termios` elsewhere. Restoring the terminal on exit is mandatory, including on `Ctrl+C`.

### Tests use synthetic fixtures

Tests are `unittest` and build a temporary store: `meta.json`, `prompt_history.json`, and a sqlite file whose root blob contains known 32-byte ids. They do not open the user's real `~/.cursor/chats`. Cover catalog ordering and scope, typed-versus-context filtering, one Agent heading across consecutive assistant messages, hidden captions by default, `--tools` captions without raw output, `--verbose` captions plus raw output, dark default, light palette, overwrite refusal, missing store, and unknown blob footer.

## Risks / Trade-offs

- [Cursor changes the undocumented store] → Check `schemaVersion`, require a root id, and put unrecognized blobs in the footer instead of failing the whole export. Tests lock the shapes observed here.
- [A future store nests messages only inside the binary checkpoint] → The direct-child rule would miss them. The reader can be extended to walk one level when a root has no JSON children; that change waits until a fixture shows it.
- [Some blobs are encrypted despite plaintext samples] → A blob whose bytes are not JSON and whose digest still matches is skipped and named. This design does not use `blobEncryptionKey`.
- [ANSI picker differs across terminals] → The export-by-id path covers the same writer without the terminal. Picker tests can drive key handling with a fake input stream.
- [Assistant Markdown outside the subset looks plain] → The subset covers fences, lists, and inline code, which is what demonstration transcripts need. The raw text remains in the file as paragraphs when a construct is unknown.

## Migration Plan

New command in an empty repository. No data migration and no rollback beyond not installing the script. The chat store is opened read-only.

## Open Questions

None. Image bytes that are not referenced by a visible turn stay in the footer until a fixture shows they belong on a turn.
