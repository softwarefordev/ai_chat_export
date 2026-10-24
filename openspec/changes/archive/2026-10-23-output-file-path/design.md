# Design

## Context

See proposal.md for why. `export_session` names the file with `safe_stem(chat.title, chat.id)` and writes it under `--out` or the current directory. The picker and `--id` both call `export_session`. One export writes one file: HTML, or Markdown when `--markdown` is set.

## Goals / Non-Goals

**Goals:**

- `--name` writes exactly the given path.
- `--name` together with `--out` writes nothing and exits unsuccessfully.

**Non-Goals:**

- Changing title-or-id names when `--name` is omitted.
- Changing how many files a no-name `--markdown` export writes.
- Rewriting the extension or running the title sanitizer on the path.
- Changing the chat title stored inside the document.

## Decisions

### The path is the file

`--name` is a path. When it is set and `--out` is not, `export_session` writes that path with `render_html` or `render_markdown`. It does not call `safe_stem` for the location and does not add an extension. A relative path is relative to the current directory. The printed path is the resolved path.

Alternative: treat `--name` as a stem and add `.html` or `.md`. The chosen parameter is a full path with an extension.

### Both flags are an error

If `--name` and `--out` are both set, the CLI prints the conflict and returns 1 before the picker or the export reads the store. No file is written.

Alternative: ignore `--out`. A directory the user typed would then have no effect.

### Parents, replacement, and directories

Create missing parent directories. `write_text` replaces an existing file. If the path exists and is a directory, or if it has no file name, print an error and return 1.

## Risks / Trade-offs

- [The path extension does not match the contents] → The extension is kept. `--markdown` chooses Markdown contents; omitting it chooses HTML contents.
- [The main spec's no-name `--markdown` case still names two files, and the code writes one] → This change does not alter that case.
- [A path contains characters the title sanitizer would remove] → The path is written as given. An operating-system error is reported if the write fails.

## Migration Plan

No store migration. `--name` is optional. Existing `--out` commands stay valid when `--name` is omitted.
