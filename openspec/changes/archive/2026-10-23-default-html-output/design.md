# Design

## Context

See proposal.md for why. `export_session` always renders HTML and Markdown from one transcript and prints both paths. `render_markdown` already produces the uncolored twin. Repeat exports replace a file that `write_text` targets. The picker and the `--id` path both call `export_session`.

`openspec/specs/session-export/spec.md` does not exist yet. The paired-output text lives in `export-agent-sessions`. The replace-on-write text lives in `overwrite-existing-output`. This delta replaces both requirements with the combined behavior.

## Goals / Non-Goals

**Goals:**

- Default export writes and prints `Title.html` only.
- `--markdown` also writes `Title.md` from that same transcript and prints both paths.
- A file this run writes is replaced if it exists. A Markdown file is left untouched when the flag is off.

**Non-Goals:**

- Removing the Markdown renderer.
- A format switch that can omit HTML.
- Changing themes, the transcript filter, or the read-only chat store.

## Decisions

### `--markdown` adds a file

Add a store-false-by-default `--markdown` flag and pass it through `export_session` from both the `--id` path and the picker path. Write and print the Markdown path only when the flag is set. HTML is always written.

Alternative: `--format html|md|both`. That can omit the page. The confirmed choice is an extra file beside the HTML page.

### Leave an unrequested Markdown file alone

When the flag is off, do not open the `.md` path. An older Markdown export stays where it is. When the flag is on, `write_text` replaces that file the same way the HTML file is replaced.

## Risks / Trade-offs

- [Scripts that expect a `.md` beside every `.html` stop seeing one] → Called out as breaking. `--markdown` restores the pair.
- [Archiving this change before `overwrite-existing-output` drops the replace behavior, or archiving overwrite afterward restores "always both files"] → Archive `export-agent-sessions`, then `overwrite-existing-output`, then this change. This requirement text includes replace-on-write.

## Migration Plan

No data migration. After implementation, a default export writes HTML only. Rollback is writing the Markdown file on every export again.

## Open Questions

None.
