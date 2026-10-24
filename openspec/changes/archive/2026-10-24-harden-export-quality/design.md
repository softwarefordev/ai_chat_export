# Design

## Context

See proposal.md for why this change exists. The requirements are in `specs/session-export/spec.md`.

`render_html._image_html` escapes the media type and inserts the payload into the `src` attribute as-is. `store.load_conversation` builds a SQLite URI by concatenating `file:`, the path, and `?mode=ro`. `safe_stem` in `__main__.py` and `_stem` in `picker.py` each strip characters Windows rejects in file names, and neither rejects reserved device names. Section headings are copied in `render_html.py` and `render_md.py`. Theme names are listed again in `argparse`.

The main spec still contains older text this change does not resolve. Project name and module invocation still say `ai-session-exporter` and `python -m session_export`. Export by chat id, and the paired HTML and Markdown requirement, still say both files are written. The code, the README, and the markdown-only behavior write one file. This design leaves that text alone.

## Goals / Non-Goals

**Goals:**

- Meet the image, store-path, and reserved-name requirements without changing ordinary titles, the four themes, or heading words.
- Give file names, headings, and theme names one definition each.
- Bring the touched modules in line with current Python practice: CapWords for the activity helper, no `assert` on the export success path, types on the public functions that lack them, and a Ruff check.

**Non-Goals:**

- A plugin or tool-caption registry.
- Rewriting blob walking in `store._add_unlinked_images`.
- Merging `main` and `export_with_picker`. Their terminals differ, and sharing them is a separate refactor.
- HTML-escaping Markdown body text.
- Adding mypy, or a formatter pass that only moves whitespace.
- Editing the stale project-name or paired-file requirements.

## Decisions

### 1. Sanitize images in the HTML renderer

`_image_html` embeds a payload only when the media type is exactly `image/png`, `image/jpeg`, `image/gif`, or `image/webp`, or `image/jpg` rewritten to `image/jpeg`. ASCII whitespace is removed, then the payload must pass `base64.b64decode(..., validate=True)`. The attribute receives the canonical base64 encoding, so a quote or angle bracket cannot remain in the tag. Any other image returns an empty string. The transcript still carries the original image; Markdown is unchanged.

Alternative considered: escape the payload with `html.escape` and keep every media type. That stops a broken tag and still embeds SVG and `text/html`, which the requirement says to omit.

### 2. Quote the database path, then append `mode=ro`

Add `sqlite_uri(path) -> str` next to `load_conversation`. It resolves the path, percent-encodes it with `/` and `:` left literal, and appends `?mode=ro`. Encoding happens before the query, so `?` and `#` in the path cannot start or end the query. `load_conversation` opens that URI. Do not add `immutable=1`; the current open mode is `mode=ro`, and immutable locking can fail on a store Cursor still has open.

Alternative considered: keep string concatenation and refuse paths that contain `?` or `#`. That rejects a real store instead of reading it.

Tests call `sqlite_uri` with a path that contains `?mode=rw` and `#`, and assert the query is only `mode=ro` and the encoded path still contains those characters. They also load a normal temporary database and compare file bytes. On an OS that can create `?` or `#` in a directory name, a load of that database must not create a file at the path truncated at that character.

### 3. One file-name function

Add `ai_chat_export/names.py` with `export_stem(title, chat_id) -> str`. It applies today's cleaning: strip, replace `<>:"/\|?*` and characters below 32 with spaces, collapse whitespace, strip trailing dots and spaces, and keep 80 characters. An empty result uses the cleaned chat id. The stem is then compared case-insensitively with `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, and `LPT1`–`LPT9`. A reserved stem uses the cleaned chat id, or that id plus `-export` when the id is reserved too. A cleaned id that is still empty uses `export`.

`__main__.py` and `picker.py` both call it. `confirm_file_name` needs the chat id: a draft whose stem is reserved becomes the id stem, not the title default. `--name` does not call it. The picker and the CLI import `names.py`, which imports nothing from this package, so there is no import cycle.

Alternative considered: leave two cleaners and call a shared reserved-name check from each. The cleaners have already drifted (only the CLI has the id fallback), so one function is the smaller rule.

### 4. One heading map and one theme list

Move the heading words to `transcript.py` as `SECTION_HEADINGS`. Both renderers import it. An unknown kind still uses the kind string.

Export the theme-name tuple from `render_html.py`. `argparse` uses that tuple for `choices`. The default stays `terminal-dark`. `render_html` still falls back to that theme when called with an unknown name.

### 5. Python practice without a type-checker gate

Rename `activity` to `Activity` and update its tests. Replace the two `assert` checks in `export_session` with a normal branch that reports an error and returns 1 if neither path was set.

Annotate the public functions that are currently untyped: `call_with_restore`, `setup_terminal`, `teardown_terminal`, `read_key`, and the callback parameters of `export_with_picker`. Use `collections.abc.Callable` and `typing.TextIO`. Do not annotate the conversation `dict` schema.

Add Ruff in `pyproject.toml` as an optional dev dependency, targeted at Python 3.11, selecting `E`, `F`, `I`, `UP`, `B`, and `N`. Do not select `ANN`. Fix what those rules report in `ai_chat_export` and `tests`.

Alternative considered: mypy in the same change. The conversation payload is untyped JSON, and a strict run would become its own project.

## Risks / Trade-offs

- [A wrapped or padded PNG stops embedding] → Whitespace is stripped before validation, and canonical base64 is what gets written. A payload that is not base64 is omitted, which is the requirement.
- [Markdown still contains a hostile image payload] → Accepted. The HTML requirement is the one that forbids script. Markdown stays the transcript text.
- [`--name CON.html` can still hit a Windows device] → Accepted. The requirement writes an explicit path as given.
- [A reserved draft falls back to the chat id, not the title] → This matches the picker scenario for `COM1`. The name line's starting value for a reserved title is already the id, so confirming it unchanged agrees with the CLI.
- [`?` in a path cannot be created on Windows] → The URI unit test runs on every OS. The live directory test runs only where the OS accepts the character.
- [Stale spec sentences get copied into this delta's modified naming requirement] → The copied sentences about also writing Markdown are the current main-spec text. This change does not re-specify which files `--markdown` writes.

## Migration Plan

No stored data and no command-line flag changes. Rollback is reverting the change. Existing exports are not rewritten.

## Open Questions

None.
