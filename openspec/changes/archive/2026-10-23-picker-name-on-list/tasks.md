# Tasks

## 1. Name line on the list

- [x] 1.1 Paint naming mode as the current list frame plus an edit line under the footer, after the id line when that line is shown. The draft line starts with `file: `, ends with a `_` cursor mark, and shows the end of a draft that is wider than the frame. The next line says typing edits the name. Up and down still leave the selection unchanged. Verify `python -m unittest tests.test_picker` passes, including a frame that still shows the selected chat, the theme, and the title file name together, a long draft that shows its end, and Esc returning to the list without the edit line.

- [x] 1.2 Say in the README that Enter asks for a file name while the chat list stays on screen. Keep the existing sentence `Enter asks for a file name.` Verify `python -m unittest tests.test_end_to_end.EndToEndTests.test_help_exits_zero` passes.

## Workflow follow-up

- Archive this change after review.
