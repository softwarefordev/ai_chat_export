# Proposal

## Why

The tool is named `ai-session-exporter` while its package is still `session_export`. Both should be `ai-chat-export`.

## What Changes

- **BREAKING**: The installed command changes from `ai-session-exporter` to `ai-chat-export`.
- **BREAKING**: `python -m session_export` changes to `python -m ai_chat_export`.
- The package directory `session_export` moves to `ai_chat_export`. A folder named `ai-chat-export` cannot be imported, so the directory uses underscores and the project name, command, help text, and README use hyphens.
- Imports in the package and in tests follow the new package name.
- The OpenSpec capability stays `session-export`. The workspace directory stays as it is. Archived change text and generated export files stay as they are.
- Archive `rename-ai-session-exporter` before this change. Its Project name and Module invocation requirements are not in the main spec yet.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The project name becomes `ai-chat-export`, and the Python module becomes `ai_chat_export`.

## Impact

- `session_export/`: the package directory, renamed to `ai_chat_export/`, and the imports inside it.
- `pyproject.toml`: project name, console script, and package include.
- `README.md`: title and documented commands.
- `tests/`: imports and the help, project-name, and README checks.
