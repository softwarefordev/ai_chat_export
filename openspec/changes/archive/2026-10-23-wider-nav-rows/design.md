# Design

## Context

See proposal.md for why. At `min-width: 52rem` the page is `16rem` plus the transcript. Each link is a row: `span.time` then `span.label`. The time is `0.75rem` and can wrap at the space. The label clips with an ellipsis. The body face is Georgia.

## Goals / Non-Goals

**Goals:**

- Give the side list a 30rem column.
- Stack the time above the prompt, at 10px, on one line.
- Set the list in a sans-serif face and leave the transcript in Georgia.

**Non-Goals:**

- Changing the compact `YY-MM-DD hh:mm` stamp, the fragment links, or the transcript type size.

## Decisions

### Widen the side column and raise the breakpoint

The two-column rule becomes `min-width: 70rem` with `grid-template-columns: 30rem minmax(0, 1fr)`. Below 70rem the list stays the full-width band it is today. A 30rem column inside the old 52rem breakpoint would leave the transcript about 22rem.

Alternative: keep 52rem and let the transcript shrink. The reading column would be the part that gets squeezed.

### Stack the entry

`nav a` is a column, so the time element comes before the label and each is on its own line. `nav .time` is `font-size: 10px` and `white-space: nowrap`. The label keeps `white-space: nowrap` and `text-overflow: ellipsis`, so the prompt uses the column width and still ends with `...`.

This replaces `nav .time { font-size: 0.75rem; }`. 10px is still smaller than the 18px prompt.

### Sans-serif on the list only

`nav` sets `font-family: "Segoe UI", system-ui, sans-serif`. The body rule keeps Georgia, so headings and the transcript do not pick up the list face.

## Risks / Trade-offs

- [Tests still expect `16rem` and `0.75rem`] → Update those assertions in the same change.
- [A 70rem window is required before the list sits beside the transcript] → Narrower windows keep the full-width band, with the same stacked rows.

## Migration Plan

A later export replaces the HTML file. No store migration.
