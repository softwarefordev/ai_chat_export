# Design

## Context

See proposal.md for why. `export_session` in `ai_chat_export/__main__.py` loads the catalog, prints warnings, reads the store, builds the transcript, renders, and writes. The first stdout line is the HTML path, after that work. The picker and `--id` both call this function. Catalog warnings already go to stderr.

## Goals / Non-Goals

**Goals:**

- Show the cycle on a terminal stderr for every quiet stretch in `export_session`.
- Clear that line before a warning, an error, or a path.

**Non-Goals:**

- A command flag, a README change, or animation on stdout.

## Decisions

### A thread on stderr, first frame immediate

A context manager writes to stderr only when `isatty()` is true. A stream with no `isatty` counts as not a terminal. It prints a newline, then `...` immediately, then replaces that line with `..` and `.` every 0.2 seconds. The first frame is immediate so a short export still shows activity. Later frames appear only while work is still going, so a fast export does not wait out the whole cycle.

The manager runs on a daemon thread because `load_conversation` and `render_html` block. Leaving the block stops the thread and writes a carriage return, spaces, and a carriage return so the next message starts on a clean line.

`export_session` uses one block around `load_catalog`, prints any warnings after that block, then uses a second block around the read, render, and write. Paths and errors are printed after the second block ends. A warning is therefore a full line, and the cycle starts again after it.

Alternative: tick only between those calls. The long waits are inside the calls, so the line would stay on one frame.

### Tests drive a short interval

The interval defaults to 0.2 seconds. Tests pass a shorter interval and a stderr whose `isatty` returns true, and they hold the work open long enough to see `...`, then `..`, then `.`. A stderr without a terminal records nothing, and stdout is still only the path.

## Risks / Trade-offs

- [The cursor is shared by stdout and stderr on a terminal] → The cycle clears its line before any path, error, or warning.
- [The picker leaves the cursor on the footer] → The cycle starts with a newline, so it does not rewrite that footer.
- [Ctrl+C during the thread] → Leaving the block always stops the thread.

## Migration Plan

No store migration. Removing the context manager restores the quiet export.
