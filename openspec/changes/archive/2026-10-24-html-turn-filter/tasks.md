# Tasks

## 1. Checkboxes and turn marks

- [x] 1.1 Mark each User section and the Agent sections that follow it until the next User section with the same turn, and verify a render test shows that mark on those sections and not on a System or Context section.
- [x] 1.2 Place an unchecked checkbox beside each User fragment link, and verify the navigator test still finds those fragment links, the boxes start unchecked, and the page contains no script and no `http`.

## 2. Filter and Clear filter

- [x] 2.1 Hide transcript sections while any box is checked and show the sections for each checked turn, and verify the stylesheet contains those rules while the chat title and footer stay outside them.
- [x] 2.2 Add Clear filter as a reset control pinned above the turn list and again after the last turn, shown only while a box is checked, and verify both controls are in the navigator and the stylesheet hides them until a box is checked.
- [x] 2.3 Leave the Markdown export unchanged, and verify a markdown render has no checkbox and no Clear filter.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
