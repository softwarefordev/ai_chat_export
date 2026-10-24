# Tasks

## 1. Safe HTML images

- [x] 1.1 In `render_html._image_html`, embed only `image/png`, `image/jpeg`, `image/gif`, and `image/webp`, rewrite `image/jpg` to `image/jpeg`, strip ASCII whitespace, require `base64.b64decode(..., validate=True)`, and write the canonical base64 encoding. Return an empty string for any other media type or payload. Verify `tests/test_render.py` covers a PNG that stays embedded, an `image/jpg` payload embedded as `image/jpeg`, a payload containing a quote and a script element that produces no `<script` and no raw breakout, and `image/svg+xml` and `text/html` payloads that are omitted.

## 2. Read-only store path

- [x] 2.1 Add `sqlite_uri` beside `load_conversation`. Resolve the path, percent-encode it with `/` and `:` left literal, append `?mode=ro`, and open that URI from `load_conversation`. Verify a unit test that a path containing `?mode=rw` and `#` produces a URI whose query is only `mode=ro` and whose encoded path still contains those characters, that loading a normal temporary database leaves its bytes unchanged, and that on an OS that allows `?` or `#` in a directory name a load does not create a database at the path truncated at that character.

## 3. Shared export file names

- [x] 3.1 Add `ai_chat_export/names.py` with `export_stem(title, chat_id)` implementing today's character cleaning, the 80-character cap, the chat-id fallback, and the reserved-device rule (`CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`, case-insensitive, with `-export` when the id is reserved, and `export` when the cleaned id is empty). Use it from `__main__.py` and from the picker's default and confirmed names. Do not apply it to `--name`. Verify `safe_stem('Map: "Maker"', "id")` is still `Map Maker`, a title `CON` exports as the chat id rather than `CON.html`, a title `nul` with `--markdown` exports as the id rather than `nul.md`, an id `CON` with no title exports as `CON-export`, a picker draft `COM1` writes the chat id rather than `COM1.html`, a picker name line for a title `CON` shows the chat id, and `--name` ending in `CON.html` writes that path.
- [x] 3.2 Note in the README that a generated name whose stem is a Windows reserved device name uses the chat id, and that `--name` is written as given. Verify the README contains that reserved-name rule and still says `--name` requires `--id`.

## 4. Shared headings and theme names

- [x] 4.1 Move the section heading words to `transcript.SECTION_HEADINGS` and use that map from `render_html` and `render_md`. An unknown kind still uses the kind string. Verify an existing HTML and Markdown render still labels a user section `User` and an agent section `Agent`.
- [x] 4.2 Export the theme-name tuple from `render_html` and use it as the `--theme` choices, keeping the default `terminal-dark` and the renderer's fallback. Verify `--help` still lists `terminal-dark`, `terminal-light`, `dark-web`, and `light-web`, and that `--theme dark` still exits unsuccessfully and writes no file.

## 5. Python practice

- [x] 5.1 Rename `activity` to `Activity`, replace the `assert` checks in `export_session` with a normal error return when neither output path was set, and annotate `call_with_restore`, `setup_terminal`, `teardown_terminal`, `read_key`, and the callback parameters of `export_with_picker`. Verify the existing activity-cycle tests pass and an export of a chat with a conversation still prints the written path.
- [x] 5.2 Add Ruff as an optional dev dependency in `pyproject.toml`, target Python 3.11, and select `E`, `F`, `I`, `UP`, `B`, and `N`. Fix what those rules report in `ai_chat_export` and `tests`. Verify `ruff check ai_chat_export tests` exits successfully.

## 6. Suite

- [x] 6.1 Run `python -m unittest discover -s tests` and verify the full suite passes.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
