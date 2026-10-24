# Design

## Context

See proposal.md for why. `run_picker` already has a naming mode. On Enter it paints `render_name_frame`, which is only `File name:` and `Enter writes  Esc returns`. The live picker clears the terminal before every frame, so that two-line frame replaces the list. Naming mode already ignores movement keys and returns to the list on Esc.

## Goals / Non-Goals

**Goals:**

- The naming frame is the current list frame with an edit line under its footer.
- The edit line shows the draft and says that typing edits it.

**Non-Goals:**

- Changing the full-screen clear used before each frame.
- Editing the name inside a title column.
- Changing how a confirmed name is sanitized, extended, or written.

## Decisions

### Append the edit line to the existing list frame

Naming mode paints the same frame as the list, including the selected row, the theme, and the id line when it is shown. Two lines follow that frame: the draft, then the hint `type to edit   Enter writes   Esc returns`. The draft line is `file: ` plus the visible draft plus a trailing `_` cursor mark. Up and down stay ignored, which the naming branch already does.

Alternative: replace the movement footer while naming. The list footer stays so the column screen does not change its existing hints. The new lines carry the edit instructions.

### A long draft shows its end

If `file: `, the draft, and the cursor mark are wider than the frame, the line keeps the rightmost characters, including the cursor mark. The columns above come from the existing list renderer and stay aligned.

Alternative: wrap the draft onto more lines. Wrapping pushes the hint down and makes the cursor harder to see.

## Risks / Trade-offs

- [Picker tests expect `File name:`] → Update those frames to expect the list, the draft, and the edit hint together.
- [The movement footer still says up and down move] → The hint under the footer is what applies while the name line is open. Movement keys still do nothing in that mode.
- [Each key still clears the terminal] → The next frame still contains the list, so the clear no longer leaves a two-line page. Leave the clear itself alone.

## Migration Plan

No store migration. A second Enter still writes the title file name. Esc still returns to the list and writes nothing.
