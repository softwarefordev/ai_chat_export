# Tasks

## 1. Named output path

- [x] 1.1 When `--name` is set and `--out` is not, write only that path from the picker and from `--id`, create missing parents, replace an existing file, and leave title-named files unwritten. A directory path exits unsuccessfully and writes nothing. Verify `python -m unittest tests.test_export tests.test_picker` passes, including a default export that still writes only the title-named HTML file.
- [x] 1.2 Reject `--name` together with `--out` before the export reads the store, and describe `--name` in `--help` and the README. Verify `python -m unittest tests.test_end_to_end.EndToEndTests.test_help_exits_zero` passes and an export test shows the conflict writes no file.

## Workflow follow-up

- Archive this change after review.
