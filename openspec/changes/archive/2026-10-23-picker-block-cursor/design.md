# Design

## Context

See proposal.md for why. `append_name_line` ends the draft with `_`. `write` in the live picker clears the screen and prints that text, so the terminal cursor is left after the hint line. `teardown_terminal` restores termios on POSIX and does nothing with the cursor. On Windows it returns immediately.

## Goals / Non-Goals

**Goals:**

- The name line places the terminal's blinking block in the cell after the visible draft.
- The list hides the cursor, and every exit path shows it again in the default shape.

**Non-Goals:**

- Blinking the cursor from a Python timer.
- Drawing a block character in the draft text.
- Changing how a confirmed name is sanitized or written.

## Decisions

### The frame text carries the cursor controls

`run_picker` appends the cursor sequence to the string it already passes to `write`. The live writer keeps clearing the screen and printing that string. Tests that collect frames can see the sequence without a terminal.

The name-line suffix shows the cursor, requests a blinking block, and moves it to the file-name row. The list-frame suffix hides the cursor. The draft text is `file: ` plus the draft, with no `_`.

Alternative: position the cursor only in `__main__.write`. The picker tests would not see the behavior, and a second writer would have to learn the row.

### A long draft keeps the last column free

The visible name line is at most one column shorter than the frame. When the draft does not fit, the line keeps the rightmost characters and the cursor occupies the last column, so it stays on the name line.

Alternative: place the cursor at column width plus one. That wraps onto the hint line.

### Restore on the way out

`teardown_terminal` shows the cursor and selects the terminal's default shape on Windows and POSIX, then restores termios when it has saved attributes. `call_with_restore` already runs that function after Esc, a finished export, and Ctrl+C.

Alternative: remember the user's previous cursor shape. The picker cannot read that shape portably, so it returns the terminal default.

## Risks / Trade-offs

- [A terminal ignores the blinking-block request] → The cursor is still in the draft cell. Its shape stays whatever that terminal uses.
- [Cursor blink is disabled in the terminal settings] → The block stays solid. The picker does not invent its own blink.
- [Tests expect a trailing `_`] → Expect the draft text and the cursor sequence instead.

## Migration Plan

No store migration. Confirming the name line still writes the same file. Esc still returns to the list.
