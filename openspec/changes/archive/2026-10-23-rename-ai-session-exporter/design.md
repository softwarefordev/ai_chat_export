# Design

## Context

See proposal.md for why. The distribution in `pyproject.toml` is `session-export`. The console script is `session-export = session_export.__main__:main`. Help sets `prog="session-export"`. The README title is `session-export` and its examples use `python -m session_export`. The import package is the directory `session_export`.

## Goals / Non-Goals

**Goals:**

- Present the project and the installed command as `ai-session-exporter`.
- Keep `python -m session_export` working.

**Non-Goals:**

- Renaming the import package, the OpenSpec capability `session-export`, or the workspace directory.

## Decisions

### Rename the distribution and the command, not the package

`pyproject.toml` sets `name = "ai-session-exporter"` and the script `ai-session-exporter = "session_export.__main__:main"`. The old script name is removed. Help uses `prog="ai-session-exporter"`, so `python -m session_export --help` still shows the new name. The README title becomes `ai-session-exporter`, and the examples name that command. They can keep a module example, because the package directory does not move.

Alternative: rename `session_export` to `ai_session_exporter`. Every import and the module command would change, and the hyphenated project name would still not match the import path.

## Risks / Trade-offs

- [Installed users still type `session-export`] → The new command is the only script. The module command remains for a checkout.
- [Help says `ai-session-exporter` while the module path says `session_export`] → The program name is the project name. The module path stays the import package.

## Migration Plan

Install the package again so the `ai-session-exporter` command replaces `session-export`. No store migration.
