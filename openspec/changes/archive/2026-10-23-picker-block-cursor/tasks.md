# Tasks

## 1. Block cursor

- [x] 1.1 Drop the `_` from the file-name line. Keep that line at most one column shorter than the frame, showing the end of a long draft. On a name frame, move the cursor to the cell after the visible draft and request a blinking block. On a list frame, hide the cursor. Verify `python -m unittest tests.test_picker` passes, including the title file name with no trailing `_`, a long draft whose name line is one column short of the width, the blinking-block sequence on the name frame, and the hide sequence on the list frame.

- [x] 1.2 On the way out of the picker, show the cursor and return it to the terminal's default shape on Windows and on POSIX. Verify a unit test covers that restore when no terminal attributes were saved and when they were.

## Workflow follow-up

- Archive this change after review.
