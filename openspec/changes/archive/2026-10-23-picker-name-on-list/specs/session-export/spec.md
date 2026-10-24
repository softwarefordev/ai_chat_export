# Spec Delta

## MODIFIED Requirements

### Requirement: Interactive picker
Running the CLI without a chat id SHALL open a picker. Up and down SHALL move the selection, left and right SHALL switch scope, Enter SHALL open a file-name line for the selected chat and SHALL NOT write a file yet, and Esc SHALL close the picker without writing files. The name line SHALL start as the title file name, or the chat id when the chat has no title. Confirming that line SHALL write the export under that file name in the output directory.

#### Scenario: Export from the picker
- **WHEN** the user presses Enter on a selected chat that has a conversation
- **THEN** the same screen still shows the selected chat and the theme, the name line shows the title file name and says that typing edits it, and no file is written yet

#### Scenario: Confirm the default name
- **WHEN** the user presses Enter on the unchanged name line
- **THEN** the title-named file is written in the output directory

#### Scenario: Edited name
- **WHEN** the user types a different file name and presses Enter
- **THEN** that file is written in the output directory and the title-named file is not written

#### Scenario: Empty name
- **WHEN** the user clears the name line and presses Enter
- **THEN** the title-named file is written in the output directory

#### Scenario: Markdown default name
- **WHEN** the user passes `--markdown` and presses Enter on a selected chat
- **THEN** the name line ends in `.md`

#### Scenario: Esc from the name line
- **WHEN** the user presses Esc on the name line
- **THEN** the chat list returns without the name line and no file is written

#### Scenario: Close without export
- **WHEN** the user presses Esc on the chat list
- **THEN** the CLI exits without writing files

## ADDED Requirements

### Requirement: Name line stays on the list
While the file-name line is open, the picker SHALL keep the chat list, the selected row, and the theme on the same screen. The name line SHALL say that typing edits the name. A draft longer than the picker width SHALL show its end, and the chat columns SHALL stay aligned. Up and down SHALL leave the selected chat unchanged while the name line is open.

#### Scenario: Long file name
- **WHEN** the draft is longer than the picker width
- **THEN** the name line shows the end of the draft and the chat columns stay aligned

#### Scenario: Movement while naming
- **WHEN** the user presses up or down while the name line is open
- **THEN** the selected chat stays the same and the list remains on screen
