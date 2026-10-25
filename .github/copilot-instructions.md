# Copilot instructions for ai-chat-export

## Build, test, and lint

This repository is a small Python CLI, so most work is validated from the repo root:

```bash
python -m pip install -e '.[dev]'
python -m ai_chat_export --help
python -m unittest tests.test_export.ExportTests.test_writes_html_path_in_out_dir
python -m unittest discover -s tests
python -m ruff check ai_chat_export tests
```

Use the single-test form when narrowing a change to one behavior. The project uses `unittest` rather than `pytest`.

## High-level architecture

The app reads local Cursor and Copilot chat sessions and exports a single, self-contained HTML or Markdown page.

- `ai_chat_export/__main__.py`: CLI entry point. It parses flags (`--id`, `--theme`, `--tools`, `--verbose`, `--detail`, `--markdown`, `--name`, `--out`, `--chats-root`), opens the picker when needed, and orchestrates exports.
- `ai_chat_export/catalog.py`: scans the local Cursor chat catalog under `~/.cursor/chats` (or a custom `--chats-root`) and builds the list of available chats, including workspace filtering and display metadata.
- `ai_chat_export/store.py`: reads the SQLite `store.db` for a selected chat, decodes Cursor's blob-based message format, and reconstructs the underlying conversation plus skipped/unlinked assets.
- `ai_chat_export/copilot_ide.py`: reads VS Code Copilot chats and Rider or Visual Studio Nitrite sessions.
- `ai_chat_export/transcript.py`: normalizes raw messages into a transcript model. This is where user/system/context/reasoning/tool-output handling, prompt splitting, and `--detail` / `--tools` / `--verbose` behavior are implemented.
- `ai_chat_export/render_html.py` and `ai_chat_export/render_md.py`: render the transcript into the final HTML or Markdown output. The HTML export is fully self-contained and embeds CSS and relevant image payloads.
- `tests/`: synthetic fixtures build ad hoc chat stores instead of reading the real user folder. Prefer matching that pattern when adding coverage.

This repo is a file-generation CLI, not a web app or service; most behavior is about preserving Cursor and Copilot chat semantics while exporting them.

## Key conventions

- Preserve the CLI contract. User-facing flags are part of the API: `--markdown` replaces HTML output with Markdown, `--name` requires `--id` and is mutually exclusive with `--out`, and existing HTML files are replaced while existing Markdown files are left alone unless Markdown export is requested.
- Prefer minimal, targeted changes at the transcript/rendering layer when adjusting export output. The architecture intentionally separates storage parsing, transcript normalization, and final output rendering.
- Keep output self-contained. HTML exports bundle CSS and image data in the generated file; do not rely on external assets.
- This project intentionally only reads local Cursor and Copilot chat data and does not mutate those stores or call Cursor or Copilot.
- Documentation and help text are part of the behavior contract. If you change CLI semantics or export defaults, update both the README and the help text that is surfaced by `python -m ai_chat_export --help`.
- The repo includes OpenSpec planning artifacts under `openspec/`; if a task is feature-oriented and the workflow expects planning, follow that structure rather than improvising a separate process.

## Validation

Before finishing a change, run the smallest relevant checks:

```bash
python -m unittest tests.test_export
python -m unittest tests.test_transcript
python -m ruff check ai_chat_export tests
```

On this repo, the focused test plus lint pass as the baseline validation loop.
