# Spec Delta

## ADDED Requirements

### Requirement: Picker columns
The picker SHALL show each chat's title, workspace folder name, and last-updated time in three columns on one row. Rows on the same page SHALL share the same column starts. The selected row SHALL keep a `>` marker. Rules SHALL separate the header from the rows and the rows from the footer.

#### Scenario: Columns line up
- **WHEN** the page shows two chats whose titles have different lengths
- **THEN** their workspace names start at the same column and their times start at the same column

#### Scenario: Selected row
- **WHEN** a chat is selected
- **THEN** that row begins with `>` and the other rows do not

### Requirement: Picker column widths
The time column SHALL have a fixed width wide enough for a two-digit day stamp, and a shorter stamp SHALL pad so it stays in that column. Last updated SHALL sit at the right edge of the time column. The workspace column SHALL match the longest workspace name on the current page, up to a cap. The title SHALL use the remaining width. A value that does not fit its column SHALL end with `...`.

#### Scenario: Time heading
- **WHEN** the picker is open
- **THEN** Last updated ends at the same column as the time stamps

#### Scenario: Long title truncates
- **WHEN** a title is wider than the title column
- **THEN** that cell ends with `...` and the workspace and time columns stay aligned

#### Scenario: Long workspace truncates
- **WHEN** a workspace name is wider than the workspace cap
- **THEN** that cell ends with `...` and the time column stays aligned

### Requirement: Selected chat id
The picker SHALL hide the selected chat id until the user presses `i`. Each press of `i` SHALL toggle that line. While the line is shown, it SHALL show the selected chat's id and SHALL follow the selection. An empty list SHALL show no id line. The footer SHALL name the `i` toggle.

#### Scenario: Hidden by default
- **WHEN** the picker opens
- **THEN** the frame has no id line and the footer names `i`

#### Scenario: Toggle on
- **WHEN** the user presses `i` and a chat is selected
- **THEN** the frame shows that chat's id

#### Scenario: Toggle off
- **WHEN** the id line is visible and the user presses `i` again
- **THEN** the id line is gone

#### Scenario: Selection moves
- **WHEN** the id line is visible and the user moves the selection
- **THEN** the line shows the newly selected chat's id

#### Scenario: Empty list
- **WHEN** the id toggle is on and the visible list is empty
- **THEN** the frame has no id line
