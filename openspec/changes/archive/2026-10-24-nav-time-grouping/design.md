# Design

## Context

See proposal.md for why. Each navigator row is a checkbox beside a link. The link stacks the turn time above the prompt with `gap: 0.15rem`. Rows have no space between them. The page font is 18px with a 1.5 line height, and the time is 10px, so the leftover leading under a prompt is larger than the gap above the next time. The time stays 10px, on one line, above its prompt. A render test rejects the substring `0.75rem` on the whole page.

## Goals / Non-Goals

**Goals:**

- Make the time sit against the prompt under it, and separate rows by a clearly larger gap.

**Non-Goals:**

- A rule or card around each row.
- Moving the time below the prompt, or changing its size or compact form.
- Changing the checkboxes, Clear filter, column width, or Markdown.

## Decisions

### Separate rows, then tighten the pair

Following rows get `margin-top: 0.85rem`. The first row gets none, so `li + li` carries the margin. The link's column gap becomes 0. The time keeps `font-size: 10px` and `white-space: nowrap`, and gains `line-height: 1`, so its box is the stamp itself and the prompt's own leading is the only space inside the pair. `0.85rem` is used because the page already rejects `0.75rem`.

Alternative: a hairline between rows. The gap alone makes the pair closer than the rows, and a line would cut through the filter list.

## Risks / Trade-offs

- [The prompt's inherited line height still leaves a few pixels under the stamp] → That remainder stays smaller than the `0.85rem` row gap.
- [The existing time rule is matched as one string] → The render test updates that string and still rejects `0.75rem`.

## Migration Plan

No store migration. A newly written page uses the tighter pair and the wider row gap. Older exports stay as they were written.
