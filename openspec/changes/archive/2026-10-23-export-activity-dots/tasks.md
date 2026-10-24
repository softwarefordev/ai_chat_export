# Tasks

## 1. Activity cycle

- [x] 1.1 Show `...`, `..`, and `.` on a terminal stderr during both quiet stretches in `export_session`, with the first frame immediate and later frames every 0.2 seconds, and verify a terminal stderr shows `...` before a successful path, an open stretch advances through `..` and `.`, and a non-terminal stderr has no frames.
- [x] 1.2 Clear the activity line before an error and before a catalog warning, then resume after the warning, and verify a missing chat shows `...` before its error line and a catalog warning stays a complete line.

## Workflow follow-up

- Archive this change after review. The delta only adds requirements, so it can merge into the existing `session-export` spec.
