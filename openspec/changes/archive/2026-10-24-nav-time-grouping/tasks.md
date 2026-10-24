# Tasks

## 1. Row spacing

- [x] 1.1 Set the navigator link gap to 0 and the turn time line height to 1, keeping the time at 10px on one line, and verify a render test finds that time rule, finds a column gap of 0, and still rejects `0.75rem`.
- [x] 1.2 Add `0.85rem` of space above every navigator entry after the first, and verify a render test finds `nav li + li { margin-top: 0.85rem; }` and the shared row rule has no top margin.
- [x] 1.3 Leave the Markdown export unchanged, and verify a markdown render of a timed user turn still shows the catalog heading and contains no `0.85rem`.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
