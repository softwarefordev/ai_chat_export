# Spec Delta

## MODIFIED Requirements

### Requirement: Name line stays on the list
While the file-name line is open, the picker SHALL keep the chat list, the selected row, and the theme on the same screen. The name line SHALL say that typing edits the name. A draft longer than the picker width SHALL show its end, and the chat columns SHALL stay aligned. Up and down SHALL leave the selected chat unchanged while the name line is open.

#### Scenario: Long file name
- **WHEN** the draft is longer than the picker width
- **THEN** the name line shows the end of the draft, leaves its last column for the cursor, and the chat columns stay aligned

#### Scenario: Movement while naming
- **WHEN** the user presses up or down while the name line is open
- **THEN** the selected chat stays the same and the list remains on screen

## ADDED Requirements

### Requirement: Block cursor on the name line
While the file-name line is open, the terminal cursor SHALL be a blinking block in the cell after the visible draft. The draft text SHALL contain no cursor character. The chat list SHALL hide the cursor. Leaving the picker SHALL show the cursor and return it to the terminal's default shape.

#### Scenario: Cursor sits on the draft
- **WHEN** the file-name line is open
- **THEN** the cursor is a blinking block in the cell after the visible draft and the draft text has no cursor character

#### Scenario: List hides the cursor
- **WHEN** the chat list is shown without the file-name line
- **THEN** the cursor is hidden

#### Scenario: Cursor is restored
- **WHEN** the picker closes, including when the user presses Esc or Ctrl+C
- **THEN** the cursor is shown in the terminal's default shape
