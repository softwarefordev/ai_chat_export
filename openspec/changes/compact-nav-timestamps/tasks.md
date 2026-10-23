# Tasks

## 1. Compact navigator time

- [x] 1.1 Reformat a parsed navigator time to YY-MM-DD hh:mm in 24-hour form, leave an unparsed time as stored, and keep the User heading on the catalog stamp, and verify a render test for `26-10-23 13:08`, `26-10-23 11:13`, `26-09-01 09:05`, `26-10-23 00:00`, `26-10-23 12:00`, an unparsed stamp, and a heading that still shows the catalog time. Update the existing navigator test that expects the catalog stamp inside the list.
- [x] 1.2 Draw the navigator time at `0.75rem` while the query stays at body size, for a parsed time and an unparsed time, and verify the stylesheet sets that size on the navigator time only.

## Workflow follow-up

- Archive this change after review. The delta only adds requirements, so it can merge into the existing `session-export` spec.
