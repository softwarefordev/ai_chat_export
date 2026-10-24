# Proposal

## Why

After Enter, the picker replaces the chat list with a two-line file-name label. That screen does not say the name can be edited, so the step looks like a new page rather than an edit of the selected chat.

## What Changes

- Enter keeps the chat list, the selected row, and the theme on screen, and adds an edit line under the footer.
- The edit line shows the draft, a cursor mark, and a hint that typing changes the name.
- A draft longer than the screen shows its end, so the cursor stays visible and the columns above stay aligned.
- Typing, Backspace, Enter, Esc, the default title name, a cleared line, and the `.md` extension stay as they are.
- Up and down do not move the selection while the edit line is open.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The interactive picker keeps the list visible while the file name is edited, and the name line says that typing edits it.

## Impact

- `ai_chat_export/picker.py` builds the name frame from the current list plus the edit line.
- `tests/test_picker.py` frames that expect a standalone `File name:` screen.
- The README sentence that describes Enter asking for a file name, so it says the list stays up.
