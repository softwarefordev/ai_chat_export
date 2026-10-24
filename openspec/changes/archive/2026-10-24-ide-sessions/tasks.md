# Tasks

## 1. Combined catalog

- [x] 1.1 Add `source` to `Chat` with default `"cli"`, and load IDE rows from `<projects-root>/<project>/agent-transcripts/<id>/<id>.jsonl` into one newest-first list. `--projects-root` defaults to `~/.cursor/projects` and replaces that default. A missing projects root adds no IDE rows and does not fail. Verify catalog tests for a transcript listed beside a different chat, newest-first order, a missing projects root, and a custom projects root.
- [x] 1.2 Apply the IDE row rules. A shared id appears once as `CLI`. The title is the first line of the first user query, or the id when that line is empty. The time is the JSONL modification time in the catalog stamp. The workspace comes from `workspacePath` in `.workspace-trusted`. A missing path shows the project folder name and This workspace omits the row. An unreadable file is omitted and stderr names its id. Verify catalog tests for each of those cases. Tests use a temporary projects root and do not open `~/.cursor/projects`.

## 2. Transcript and export

- [x] 2.1 Adapt `user` and `assistant` lines into the messages `build_transcript` already accepts. Map `tool_use` to a `tool-call` with `toolName` and `args`. Skip `turn_ended` with no section. Name any other line in the footer as `line N` and omit it from the body. Pass inner `user_query` strings as the prompts. Verify a fixture with two assistant lines around `turn_ended` produces one Agent heading, a bad line is named in the footer and absent from the body, and `--tools` captions a Shell call with its short description and without the command text.
- [x] 2.2 Export an IDE id through the existing HTML or Markdown path, and export the agent chat when the id exists in both stores. Leave the JSONL file and `.workspace-trusted` unchanged. The written page shows the session title and workspace and omits the source cell. An empty transcript still reports that the chat has no transcript. Verify export tests for an IDE `--id`, a shared id whose IDE-only query is absent, unchanged file bytes, and an HTML page that contains the title and workspace and does not contain `CLI` or `IDE` when the fixture text uses neither word.

## 3. Picker and README

- [x] 3.1 Render the source column between the workspace and the time, three characters wide, `CLI` or `IDE`, with two spaces around it. Keep `Last updated` right-aligned in the time column. Update the wide-workspace slice so it still reads the 24-character workspace cell. Verify a picker test at an explicit width that workspace, source, and time share column starts, that an agent chat reads `CLI` and a transcript reads `IDE`, and that the header still ends with `Last updated`.
- [x] 3.2 Document the combined list and `--projects-root` in the README. The list sentence names the source column. Verify the README contains that sentence and `--projects-root`, still contains `Enter asks for a file name.` and `HTML is the default.`, and does not contain `writes nothing`. Verify help mentions `--projects-root`.

## 4. Integration

- [x] 4.1 Run `python -m unittest discover` and verify the suite passes.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
