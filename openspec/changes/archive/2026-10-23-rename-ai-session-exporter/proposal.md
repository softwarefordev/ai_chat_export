# Proposal

## Why

The tool is presented as `session-export`. It should be named `ai-session-exporter`.

## What Changes

- **BREAKING**: The installed command changes from `session-export` to `ai-session-exporter`.
- The project name, help program name, and README title become `ai-session-exporter`.
- `python -m session_export` still runs the tool. The import package stays `session_export`.
- The OpenSpec capability stays `session-export`. The workspace directory stays as it is.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The tool presents itself as `ai-session-exporter`, and the installed command uses that name.

## Impact

- `pyproject.toml`: project name and console script.
- `session_export/__main__.py`: help program name.
- `README.md`: title and the documented command.
- `tests/test_end_to_end.py`: help and README use the new name.
