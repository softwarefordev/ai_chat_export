# Tasks

## 1. Package directory

- [x] 1.1 Move `session_export/` to `ai_chat_export/`, rewrite `session_export` imports in the package and in tests, point the help test at `python -m ai_chat_export`, and verify `python -c "import ai_chat_export"` succeeds and `python -m unittest discover` passes.

## 2. Project name

- [x] 2.1 Set the project name and console script to `ai-chat-export` with entry `ai_chat_export.__main__:main`, set help `prog` to `ai-chat-export`, update the help and project-file checks, and verify `python -m ai_chat_export --help` prints `usage: ai-chat-export` and exits 0.
- [x] 2.2 Title the README `ai-chat-export`, document that command and `python -m ai_chat_export`, update the README checks, and verify the README heading and `python -m unittest tests.test_end_to_end.EndToEndTests.test_help_exits_zero` pass.

## Workflow follow-up

- Archive `rename-ai-session-exporter` before this change so Project name and Module invocation are in the main spec.
- Archive this change after review. The delta modifies those two requirements.
