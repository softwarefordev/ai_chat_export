# Tasks

## 1. Package scaffold

- [x] 1.1 Add `pyproject.toml` for package `session_export` with script `session-export` and no third-party dependencies. Verify `python -m session_export --help` exits 0.
- [x] 1.2 Add importable modules `catalog`, `store`, `transcript`, `render_html`, `render_md`, `picker`, and `__main__`. Verify `python -c "import session_export"` succeeds.

## 2. Chat catalog

- [x] 2.1 Load chats from a directory of `meta.json` files with title, workspace folder name, local timestamp `Aug 15, 2026 04:42 PM`, newest-first sort, unsupported `schemaVersion` warnings, and missing `store.db` kept as listable. Verify unit tests cover a titled chat, a missing title, sort order, an unsupported schema, and unreadable metadata.
- [x] 2.2 Filter This workspace by normalized path, case-insensitive on Windows. Verify a unit test keeps only chats whose `cwd` is the launch directory.

## 3. Conversation store and transcript

- [x] 3.1 Open `store.db` read-only, decode the hex meta row, and walk 32-byte ids in the root blob, keeping each direct JSON message once. Verify a synthetic fixture returns messages in order and does not repeat the checkpoint child.
- [x] 3.2 Build the default transcript: typed prompts, assistant text, and captions for `Read`, `Glob`, and `Shell`. Verify tests show typed text without injected context, a path caption, a pattern caption, a description caption, and no command text or tool result.
- [x] 3.3 Add verbose sections and the footer for unrecognized blobs and images that no visible turn references. Verify tests include system text, reasoning, raw tool output, a skipped-blob footer line, and an unlinked image named only in the footer.

## 4. HTML and Markdown rendering

- [x] 4.1 Render the assistant subset: fenced code, lists, paragraphs, and inline code. Verify unit tests for those four constructs.
- [x] 4.2 Write one self-contained HTML file with either the dark or the light palette inlined, no script, and no external URL. Verify tests that the default palette is dark, `--theme light` selects the light palette, and the file contains no `http` URL.
- [x] 4.3 Write Markdown with the same prompts, assistant text, and tool captions and with no color tokens. Verify a test that those turns match the HTML text.

## 5. Export command

- [x] 5.1 Implement `--id`, `--theme`, `--verbose`, `--out`, sanitized file names, overwrite refusal, unknown id, and metadata-only chats. Verify a temp-store test checks both printed paths, the current directory, `--out`, a conflict that writes nothing, a missing conversation, and an unknown id.
- [x] 5.2 Keep the chat store unchanged during export. Verify a test that the fixture `store.db` bytes are identical after a successful export.
- [x] 5.3 Document `session-export` usage in `README.md`. Verify the documented `python -m session_export --help` command runs.

## 6. Session picker

- [x] 6.1 Draw the ANSI list from a fake input stream: up and down, left and right for scope, Enter, Esc, Backspace, and a theme footer. Verify tests for movement, scope, Enter returning the selected id, Esc returning no selection, Backspace not signaling a delete, and a footer of `theme: dark` or `theme: light`.
- [x] 6.2 Connect the picker to export and restore terminal settings on exit, including `Ctrl+C`. Verify a fake-IO test that Enter writes both files, Esc writes none, and the restore hook runs.

## 7. End-to-end check

- [x] 7.1 Run the full unit suite and one `--id` export of the synthetic fixture. Verify `python -m unittest discover` passes and the written HTML is a single file whose body contains the fixture's typed prompt and assistant text.

## 8. Bundle agent stretches and optional tools

- [x] 8.1 Collapse consecutive assistant messages, reasoning, and tool results into one Agent section until the next typed prompt. Omit the section when it would have no visible text and no visible captions. Verify a unit test that two assistant messages before the next prompt produce one Agent heading in HTML and Markdown, and that a tools-only stretch produces none on a default export.
- [x] 8.2 Add `--tools`. A default export omits captions. `--tools` includes captions and omits raw tool output. `--verbose` includes captions and raw tool output inside the same Agent section. Verify tests for all three modes, including that a command caption still omits the command text.
- [x] 8.3 Document `--tools` in `README.md`. Verify the documented `python -m session_export --help` output mentions `--tools`.
