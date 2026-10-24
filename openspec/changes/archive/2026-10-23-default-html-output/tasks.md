# Tasks

## 1. HTML by default

- [x] 1.1 Write and print only the HTML file from `export_session` unless Markdown is requested, and verify a fresh `--id` export, the end-to-end export, and the picker export each leave no Markdown file and print the HTML path.
- [x] 1.2 Leave an existing Markdown file unchanged while replacing an existing HTML file, and verify an export test that the HTML file contains the new transcript, the Markdown file still has its old text, and a neighboring file is unchanged.

## 2. Markdown flag

- [x] 2.1 Add `--markdown` on the `--id` path and the picker path so the command also writes and prints `Title.md` from the same transcript, replacing either file that already exists, and verify an export test that both paths are printed, the Markdown file contains the visible turns, and it contains no color hex from the HTML theme.
- [x] 2.2 Document HTML as the default and `--markdown` as the extra file in the README and in `--help`, and verify `session-export --help` lists `--markdown` and the README describes that default.

## Workflow follow-up

- Archive `export-agent-sessions`, then `overwrite-existing-output`, before this change so the base requirements exist and the replace-on-write behavior is already in the main spec.
- Archive `default-html-output` after review.
