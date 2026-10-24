# Tasks

## 1. Markdown-only export

- [x] 1.1 When `write_markdown` is set, write and print only the Markdown file, leave an existing HTML file unchanged, and still replace an existing Markdown file. Verify `tests.test_export` and `tests.test_picker` pass, including a default export that still writes only HTML.
- [x] 1.2 Describe `--markdown` as the Markdown export in `--help` and the README, and verify `python -m unittest tests.test_end_to_end.EndToEndTests.test_help_exits_zero` passes.

## Workflow follow-up

- Archive `export-agent-sessions`, then `overwrite-existing-output`, then `default-html-output`, before this change so the modified requirements are in the main spec.
- Archive this change after review.
