# session-export Specification

## Purpose

Export AI development tool chat sessions into a documentation or demo worthy format.

## Requirements

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

### Requirement: Distinct turn panels
The HTML page SHALL paint each User section and each Agent section with different panels. A User panel SHALL use a warm background and a gold edge. An Agent panel SHALL use a cooler, flatter background. A System or Context section SHALL NOT use the User panel or the Agent panel.

#### Scenario: User and Agent differ
- **WHEN** the page contains a User section and an Agent section
- **THEN** those sections use different panel backgrounds

#### Scenario: Both themes keep the difference
- **WHEN** the same transcript is exported in the dark theme and the light theme
- **THEN** each file paints the User panel and the Agent panel differently

#### Scenario: Other sections stay quiet
- **WHEN** the page contains a System or Context section
- **THEN** that section uses neither the User panel nor the Agent panel

### Requirement: User-turn navigator
The HTML page SHALL include a navigator that stays in view while the transcript scrolls. The navigator SHALL link to each User section with a fragment in the same file. It SHALL NOT link to Agent, System, or Context sections. A transcript with no User section SHALL show no navigator entries. The page SHALL contain no script and no external address.

#### Scenario: Links reach user turns
- **WHEN** the page contains two User sections and one Agent section
- **THEN** the navigator has a fragment link to each User section and no link to the Agent section

#### Scenario: Empty transcript
- **WHEN** the transcript has no User section
- **THEN** the navigator has no entries

#### Scenario: Stays in the file
- **WHEN** the page is written
- **THEN** each navigator link is a fragment in that file, and the page contains no script and no external address

### Requirement: Navigator entries
Each navigator entry SHALL show that User section's turn time when it has one, and the query text up to its first line break. An entry SHALL clip that text with an ellipsis when it does not fit. A User section with no query text SHALL still have an entry. The User section opened from the navigator SHALL be marked.

#### Scenario: Time and first line
- **WHEN** a User section has a turn time and a query with more than one line
- **THEN** its entry shows the turn time and the text before the first line break, and omits the later lines

#### Scenario: Long line clips
- **WHEN** a User section's first line does not fit the entry
- **THEN** the entry clips that line with an ellipsis

#### Scenario: No query text
- **WHEN** a User section has no query text
- **THEN** the navigator still has an entry that links to that section

#### Scenario: Opened section is marked
- **WHEN** the reader opens a navigator entry
- **THEN** that User section is marked

### Requirement: Navigator column
When the page is wide enough for the list to sit beside the transcript, the navigator column SHALL be 30rem. On a narrower page the navigator SHALL span the width above the transcript.

#### Scenario: Wide page
- **WHEN** the page is at least 70rem wide
- **THEN** the navigator column is 30rem beside the transcript

#### Scenario: Narrow page
- **WHEN** the page is narrower than 70rem
- **THEN** the navigator spans the width above the transcript

### Requirement: Navigator row stack
Each navigator entry SHALL place the turn time on its own line above the prompt. The time SHALL stay on one line.

#### Scenario: Time above the prompt
- **WHEN** an entry has a turn time and a prompt
- **THEN** the time is on the line above the prompt

#### Scenario: Time stays on one line
- **WHEN** the navigator shows a turn time
- **THEN** that time does not wrap onto a second line

### Requirement: Navigator type
The navigator time SHALL be 10px. The navigator SHALL use a sans-serif face. The transcript SHALL keep its serif face.

#### Scenario: Time is 10px
- **WHEN** the navigator shows a turn time
- **THEN** that time is 10px

#### Scenario: Navigator face
- **WHEN** the page is written
- **THEN** the navigator uses a sans-serif face and the transcript keeps its serif face

### Requirement: Project name
The tool SHALL present itself as `ai-session-exporter` in help text and in the README. The installed command SHALL be `ai-session-exporter`.

#### Scenario: Help names the tool
- **WHEN** the user asks for help
- **THEN** the usage line names `ai-session-exporter`

#### Scenario: README names the tool
- **WHEN** the README is read
- **THEN** its title is `ai-session-exporter`

#### Scenario: Installed command
- **WHEN** the package declares its console command
- **THEN** that command is `ai-session-exporter`

### Requirement: Module invocation
Invoking the tool as a Python module SHALL still run it.

#### Scenario: Module entry
- **WHEN** the user runs `python -m session_export`
- **THEN** the tool runs

### Requirement: Export activity cycle
When stderr is a terminal, an export SHALL show a repeating cycle of `...`, `..`, and `.` on stderr during its quiet work, from the start of the export until it reports a result.

#### Scenario: Cycle before the path
- **WHEN** an export writes a file and stderr is a terminal
- **THEN** stderr shows `...` before the path is printed

#### Scenario: Cycle advances while work continues
- **WHEN** the export is still working and stderr is a terminal
- **THEN** the frames advance in order through `...`, `..`, and `.`

#### Scenario: Cycle before an error
- **WHEN** an export fails and stderr is a terminal
- **THEN** stderr shows `...` before the error

### Requirement: Activity line clears
The activity cycle SHALL be cleared before a path, an error, or a catalog warning is written.

#### Scenario: Path replaces the cycle
- **WHEN** the export prints a path
- **THEN** the activity line is cleared before that path

#### Scenario: Error replaces the cycle
- **WHEN** the export prints an error
- **THEN** the activity line is cleared before that error

#### Scenario: Warning stays intact
- **WHEN** the export prints a catalog warning
- **THEN** that warning is a complete line and the cycle resumes after it

### Requirement: Quiet when stderr is not a terminal
When stderr is not a terminal, the activity cycle SHALL write nothing.

#### Scenario: Piped stderr
- **WHEN** an export runs and stderr is not a terminal
- **THEN** stderr contains no activity frame
