# Proposal

## Why

A long export shows every turn at once. A reader who wants a few prompts and the replies that follow them has to scroll past the rest.

## What Changes

- Each navigator entry gains a checkbox beside its fragment link. Nothing starts checked, and the whole transcript stays visible.
- Checking one or more boxes hides the other transcript sections. Each checked User section stays, with the Agent sections that follow it until the next User section.
- System and Context sections stay hidden while any box is checked. The chat title, the footer, and the full navigator stay.
- Clear filter appears at the top of the navigator, pinned above the list, and again after the last turn. Both show only while a box is checked, and either one returns every turn.
- The page still has no script and no external address. Markdown is unchanged.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The HTML navigator can filter the transcript to selected User sections and the Agent sections that follow them, and Clear filter restores every turn.

## Impact

- `ai_chat_export/render_html.py` adds the checkboxes, the two reset controls, and the style rules that show and hide sections.
- `tests/test_render.py` checks the filter markup and that the page still has no script and no external address.
