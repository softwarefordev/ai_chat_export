# Design

## Context

See proposal.md for why. The HTML page is one file. The navigator is a sticky list of fragment links to User sections, and the page is required to contain no script and no external address. Agent sections already follow their User section until the next User section. System and Context are separate sections. The chat title and the footer are not those sections.

## Goals / Non-Goals

**Goals:**

- Checking boxes shows only the marked User sections and the Agent sections that follow them.
- Both Clear filter controls reset those boxes without a script.

**Non-Goals:**

- Filtering the navigator list itself.
- Changing the Markdown export.
- Adding a script or an external address.

## Decisions

### Style rules react to the checkboxes

The boxes and both Clear filter controls live in one form in the navigator. Each control is a reset button, so either one restores the unchecked state. The top button is the first item in the scrolling navigator and sticks to its top. The bottom button follows the last entry.

Each User section and the Agent sections after it, until the next User section, share a turn mark. While any box is checked, transcript sections are hidden, and each checked box shows the sections with its mark. System and Context sections have no mark, so they stay hidden. The title and the footer are not sections, so they stay.

Alternative: filter with a script. The page is required to contain none.

### The link stays beside the checkbox

The checkbox is a sibling of the fragment link, not wrapped around it. Checking a turn leaves the jump intact.

Alternative: make the whole row the checkbox label. That mixes checking with navigating.

## Risks / Trade-offs

- [An older browser ignores the checked-box rule] → The boxes and Clear filter are still present, and every turn stays visible.
- [A long chat adds one style rule per User section] → The rules stay in the same file. They name turns that are already on the page.
- [Tests reject `http` and a script element] → The filter markup uses neither.

## Migration Plan

No store migration. An export written before this change has no checkboxes. A new export shows every turn until a box is checked.
