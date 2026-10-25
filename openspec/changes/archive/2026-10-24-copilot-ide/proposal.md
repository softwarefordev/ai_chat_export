# Proposal

## Why

Copilot CLI sessions are already in the catalog, and Copilot chats from VS Code, Rider, and Visual Studio still sit in separate local stores. Those IDE sessions should join the same list and the same HTML or Markdown export, under one filter.

## What Changes

- Add one registry row for every Copilot IDE host: stored id `cp-ide`, `--source copilot-ide`, filter label `Copilot-IDE`, column `Cp-IDE`. VS Code, Rider, and Visual Studio share that cell.
- Read VS Code version-3 chat sessions, Rider sessions under the local `github-copilot/rd/chat-agent-sessions` store, and Visual Studio sessions under `github-copilot/vs` when that directory exists. `--vscode-root` and `--copilot-ide-root` replace the defaults. A missing root adds no rows and does not fail.
- A current VS Code or Rider chat may keep its transcript in a Copilot event log. A VS Code agent-host link and a Rider conversation id claim that log as one `Cp-IDE` row. An event log that no IDE row claims, and that the Copilot CLI database does not list, still joins the catalog as `Cp-CLI`.
- Leave a session out of the list when it has no user message and no assistant text. Keep a Copilot IDE row when its id also exists as a Cursor or Copilot CLI session.
- Export the turn text through the existing HTML or Markdown path. The written page omits the source cell. `--tools` adds captions and omits tool results and command text.
- Extend the source line and the `s` cycle with Copilot-IDE after Copilot-CLI. Passing only the two Cursor `--source` values still omits every Copilot row, and the next `s` returns to All sources.
- Describe the tool as exporting Cursor and Copilot sessions in the README, the package description, the contributor instructions, and the command help.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The catalog, picker, export, and product description include Copilot IDE sessions from VS Code, Rider, and Visual Studio under one `Cp-IDE` cell.

## Impact

- Catalog merge, a Copilot IDE reader, the source registry, picker cycle, `--vscode-root`, and `--copilot-ide-root`. README, package description, contributor instructions, help, and tests change. The reader also follows VS Code agent-host links and Rider conversation ids into Copilot event logs, and lists any remaining unlisted event log as Copilot CLI.
- HTML and Markdown stay on the existing path. The source cell stays off the written page. The reader uses the Python standard library, including for the Rider and Visual Studio Nitrite store.
