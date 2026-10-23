# Proposal

## Why

Navigator stamps use the long catalog form, such as `Oct 23, 2026 11:13 AM`, so the time crowds the query line.

## What Changes

- A parsed navigator time is `YY-MM-DD hh:mm` with a two-digit year, zero-padded month and day, and a 24-hour clock. `Oct 23, 2026 01:08 PM` becomes `26-10-23 13:08`.
- That navigator time uses a smaller font than the query text beside it.
- A turn time that cannot be parsed stays as stored and still uses the smaller font.
- User and Agent headings, Markdown, the picker, and the chat header keep the catalog time. Assumption: the clock is 24-hour because the requested pattern has no AM/PM.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: Navigator entries show a compact turn time in a smaller font. Headings keep the catalog time.

## Impact

- `session_export/render_html.py`: format and size of the navigator time only.
- `tests/test_render.py`: compact stamps, the smaller navigator font, an unparsed stamp, and an unchanged heading.
