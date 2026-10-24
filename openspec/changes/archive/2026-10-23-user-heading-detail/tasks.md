# Tasks

## 1. Query only

- [x] 1.1 Treat `user_query` inner text as the query, keep plain typed text that has no elements, and omit a message that is only a `conversation_summary`, and verify a transcript unit test for each of those three cases.
- [x] 1.2 Omit a message that is only injected context such as `user_info`, and verify a transcript unit test that the default export has no User section for it and that `--verbose` still includes that context.

## 2. Detail blocks

- [x] 2.1 Show `conversation_summary` and `cursor_commands` inner text once after the query when `--detail` is set, show a summary-only message only then, and keep both out of the verbose context when both flags are set, and verify transcript unit tests for a query plus each block, a summary-only message, and both flags together.
- [x] 2.2 Document that `--detail` adds the conversation summary and the command block, and verify the README says that and `session-export --help` still lists `--detail`.

## 3. User heading

- [x] 3.1 Label the user section User in HTML and Markdown while the agent section stays Agent, and verify render tests that a query's HTML heading is User, its Markdown heading is User, and an agent stretch heading is Agent.
- [x] 3.2 Document the User label in the README, and verify the README says the user section is labeled User.

## Workflow follow-up

- Archive `export-agent-sessions`, then `user-turn-detail`, before this change so the requirements being modified exist in the main spec.
- Archive `user-heading-detail` after review.
