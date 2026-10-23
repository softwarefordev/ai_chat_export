# Tasks

## 1. Replace existing exports

- [x] 1.1 Remove the existence check in `export_session` so a repeat export replaces `{stem}.html` and `{stem}.md`, and verify an export test where both files already contain old text: the command exits 0, prints both paths, and both files contain the new transcript.
- [x] 1.2 Cover the HTML-only case and a neighboring file in that test, and verify the HTML file is replaced, the Markdown file is created, both contain the new transcript, and the neighboring file is unchanged.
- [x] 1.3 Update the README so it says an existing HTML or Markdown target is replaced, and verify that sentence is present and the README no longer says the command writes nothing.

## Workflow follow-up

- Archive `export-agent-sessions` before this change so `openspec/specs/session-export/spec.md` exists for the modified requirement.
- Archive `overwrite-existing-output` after review.
