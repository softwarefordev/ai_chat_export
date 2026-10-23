# Design

## Context

See proposal.md for why. The package directory is `session_export`. Its modules import that name: `__main__`, `catalog`, `picker`, `render_html`, `render_md`, and `transcript`. Tests import it from `test_catalog.py`, `test_end_to_end.py`, `test_export.py`, `test_picker.py`, `test_render.py`, and `test_transcript.py`. `pyproject.toml` names the project `ai-session-exporter`, points the console script at `session_export.__main__:main`, and includes `session_export*`. Help sets `prog="ai-session-exporter"`.

## Goals / Non-Goals

**Goals:**

- One package directory, `ai_chat_export`, and one command, `ai-chat-export`.
- Imports, help, the README, and tests use those names.

**Non-Goals:**

- Renaming the OpenSpec capability `session-export`, the workspace directory, archived change text, or generated export files.

## Decisions

### Underscores for the package directory

Move `session_export/` to `ai_chat_export/` and replace every `session_export` import in the package and in tests. Python import names cannot contain a hyphen, so the directory cannot be `ai-chat-export`.

`pyproject.toml` sets `name = "ai-chat-export"`, the script `ai-chat-export = "ai_chat_export.__main__:main"`, and `include = ["ai_chat_export*"]`. The old script entry is removed. Help uses `prog="ai-chat-export"`. The README title and examples use `ai-chat-export`, and the checkout example uses `python -m ai_chat_export`.

Alternative: keep the directory as `session_export` and only rename the command. That leaves the package name the user asked to change.

## Risks / Trade-offs

- [An installed `ai-session-exporter` command remains] → Reinstall the package. The new script is the only console entry.
- [`rename-ai-session-exporter` is still unarchived] → Archive that change before this one so Project name and Module invocation exist in the main spec for this delta to modify.

## Migration Plan

Rename the package directory, update imports and the project metadata, then install the package again. No store migration. Restoring the old directory name and the `ai-session-exporter` script rolls the rename back.
