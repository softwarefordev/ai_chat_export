# Design

## Context

See proposal.md for why. `format_datetime` writes the catalog stamp `Oct 23, 2026 11:13 AM`, with a locale month, a day that is not zero-padded, and a zero-padded 12-hour clock. `block.timestamp` already holds that stamp. The navigator prints it in `span.time`, and the User heading uses the same class for color. The picker, the chat header, and Markdown use the catalog stamp too.

## Goals / Non-Goals

**Goals:**

- Reformat a parsed catalog stamp for the navigator only.
- Draw that navigator time smaller than the query text.

**Non-Goals:**

- Changing `format_datetime`, the picker, the chat header, Markdown, or the User and Agent headings.

## Decisions

### Parse the catalog stamp in the navigator

The navigator parses `block.timestamp` with the catalog shape: locale month, day, four-digit year, zero-padded 12-hour clock, and AM/PM. A match becomes `YY-MM-DD hh:mm` in 24-hour form, with the year, month, day, hour, and minute zero-padded. `12:00 AM` is `00:00` and `12:00 PM` is `12:00`. A stamp that does not match is shown as stored.

The month is parsed with the same `%b` the catalog used, so the conversion stays in the process locale.

Alternative: store a second timestamp on the block. The heading and the navigator would then diverge in the transcript model. Parsing at render time leaves the stored stamp alone.

### Smaller type on the navigator time only

`nav .time` sets `font-size: 0.75rem`. The query stays at the body size. The shared `.time` color rule stays, so heading times keep their size and only the navigator time shrinks.

Alternative: shrink the whole navigator. The query line would lose room it does not need to give up.

## Risks / Trade-offs

- [A locale whose `%b` does not match the stored month] → The stamp stays as stored, which is the unparsed rule.
- [`12` AM and PM are easy to leave on a 12-hour clock] → The tests cover midnight and noon.

## Migration Plan

A later export replaces the HTML file. No store migration.
