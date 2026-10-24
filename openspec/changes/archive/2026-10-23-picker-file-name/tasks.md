# Tasks

## 1. Picker file-name line

- [x] 1.1 After Enter on a chat, show a file-name line that starts as the title file name, or the chat id when there is no title, and ends in `.md` when Markdown is requested. A second Enter writes that name in the output directory. Typing then Enter writes the edited name and not the title-named file. A cleared line uses the title file name. Esc returns to the list and writes nothing. The list footer says Enter names the file. Verify `python -m unittest tests.test_picker` passes, including the existing export that confirms the default name.

## 2. `--name` stays on `--id`

- [x] 2.1 Reject `--name` without a chat id before the picker opens, and do not pass that flag into the picker export. An `--id --name` export still writes that path. Describe the picker name line and that `--name` requires `--id` in the README and `--help`. Verify `python -m unittest tests.test_export tests.test_end_to_end.EndToEndTests.test_help_exits_zero` passes, including a run where `--name` without `--id` writes no file.

## Workflow follow-up

- Archive and sync `output-file-path` before this change, so its `--id` path rules are in the main spec first.
- Archive this change after review.
