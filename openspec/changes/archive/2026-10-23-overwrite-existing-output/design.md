# Design

## Context

See proposal.md for why. `export_session` builds the two paths from the sanitized title, and if either path exists it prints `Export already exists` and returns 1 before creating the directory or writing. `Path.write_text` already replaces a file that exists. The chat database is opened read-only and is outside this check.

The requirement being modified lives in the unarchived `export-agent-sessions` delta. `openspec/specs/session-export/spec.md` does not exist yet.

## Goals / Non-Goals

**Goals:**

- A repeat export to the same paths replaces the HTML file, the Markdown file, or both, and still prints both paths.
- A file in the output directory that is not one of those two paths stays untouched.

**Non-Goals:**

- A prompt, a backup copy, or a `--force` flag.
- Changing file names, the picker, or the read-only chat store.

## Decisions

### Replace in place, with no new flag

Delete the existence check. Keep the directory create and the two `write_text` calls. An existing file is replaced because that is what `write_text` does. The command stays successful and prints both paths, matching a first export.

Alternative: add `--force` and keep the refusal as the default. The request is to overwrite on output, so a second flag would leave the current refusal in the way of a re-export.

### Leave every other file alone

The only paths written are `{stem}.html` and `{stem}.md` in the output directory. Nothing else in that directory is deleted or renamed.

## Risks / Trade-offs

- [A previous export at those paths is discarded] → That is the requested behavior. The chat store is not one of those paths.
- [The HTML write succeeds and the Markdown write then fails, leaving a mixed pair] → Same window as a first export. No extra staging.

## Migration Plan

No data migration. After implementation, a repeat export replaces the previous files. Rollback is restoring the existence check.

## Open Questions

None.
