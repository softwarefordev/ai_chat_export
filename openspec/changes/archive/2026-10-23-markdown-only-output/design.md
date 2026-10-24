# Design

## Context

See proposal.md for why. `export_session` always renders HTML, writes `{stem}.html`, prints that path, and when `write_markdown` is set also writes `{stem}.md` and prints that path. `--help` says "Also write a Markdown file beside the HTML page." The README says the same. The picker and `--id` both pass `args.markdown` into `export_session`.

## Goals / Non-Goals

**Goals:**

- `--markdown` writes and prints only the Markdown file.
- A default export still writes and prints only HTML.

**Non-Goals:**

- Deleting an HTML file that is already in the output directory.
- A second flag that writes both files.

## Decisions

### One file per export

When `write_markdown` is set, `export_session` builds the same transcript, writes `{stem}.md`, and prints that path. It does not call the HTML renderer and does not open `{stem}.html`. An existing HTML file is left byte for byte. An existing Markdown file is still replaced by the write.

When `write_markdown` is unset, the HTML path stays as it is today.

`--help` and the README say `--markdown` writes the Markdown file. The description no longer says the HTML page is also written.

Alternative: delete a sibling HTML file when Markdown is requested. The request is to skip the HTML export. Removing a file the user already has is a separate action.

## Risks / Trade-offs

- [A previous `--markdown` run left an HTML file next to the Markdown file] → This export leaves that HTML file in place. Run without `--markdown` to replace it.
- [`default-html-output` is still unarchived] → Archive `export-agent-sessions`, then `overwrite-existing-output`, then `default-html-output`, before this change, so the modified requirements exist in the main spec.

## Migration Plan

No store migration. Callers that passed `--markdown` and read the HTML path should run once without the flag to refresh the HTML file.
