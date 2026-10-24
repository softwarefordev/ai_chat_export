# Spec Delta

## MODIFIED Requirements

### Requirement: Picker columns
The picker SHALL show each session's title, workspace folder name, source, and last-updated time in four columns on one row. The source column SHALL sit between the workspace and the time, SHALL be six characters wide, and SHALL read `Cu-CLI` for an agent chat and `Cu-IDE` for an IDE transcript. Rows on the same page SHALL share the same column starts. The selected row SHALL keep a `>` marker. Rules SHALL separate the header from the rows and the rows from the footer.

#### Scenario: Columns line up
- **WHEN** the page shows two sessions whose titles have different lengths
- **THEN** their workspace names start at the same column, their source cells start at the same column, and their times start at the same column

#### Scenario: Selected row
- **WHEN** a session is selected
- **THEN** that row begins with `>` and the other rows do not

#### Scenario: Source cells
- **WHEN** the page shows an agent chat and an IDE transcript
- **THEN** the agent chat's source cell is `Cu-CLI` and the transcript's source cell is `Cu-IDE`

### Requirement: Shared session listed once
An id that exists as an agent chat and as an IDE transcript SHALL appear once, from the agent chat, with source `Cu-CLI`.

#### Scenario: Same id in both stores
- **WHEN** the same id is in the chat catalog and in an IDE transcript
- **THEN** the list has one row for that id and its source cell is `Cu-CLI`

## ADDED Requirements

### Requirement: Source filter line
The picker SHALL show a source line under the workspace scope. The line SHALL name All sources, Cursor-CLI, and Cursor-IDE. It SHALL mark All sources when every source is allowed, and SHALL mark each allowed source when the filter is a subset.

#### Scenario: Open on every source
- **WHEN** the picker opens without `--source`
- **THEN** the source line marks All sources

#### Scenario: One source is marked
- **WHEN** the active filter allows only agent chats
- **THEN** the source line marks Cursor-CLI and does not mark All sources

### Requirement: Source filter key
Pressing `s` on the chat list, in either case, SHALL cycle the filter through All sources, Cursor-CLI, and Cursor-IDE, then back to All sources. The selection SHALL return to the first visible row. The footer SHALL name `s`.

#### Scenario: Cycle to Cursor-CLI
- **WHEN** All sources is active and the user presses `s`
- **THEN** Cursor-CLI is active and the first visible row is selected

#### Scenario: Cycle back to All sources
- **WHEN** Cursor-IDE is active and the user presses `s`
- **THEN** All sources is active

### Requirement: Source key on the name line
While the file-name line is open, `s` SHALL be typed into the draft and SHALL leave the source filter unchanged.

#### Scenario: Typing s
- **WHEN** the file-name line is open and the user presses `s`
- **THEN** the draft gains `s` and the source filter is unchanged

### Requirement: Source filter with workspace scope
The source filter and the workspace scope SHALL both apply. Left and right SHALL keep switching All chats and This workspace without changing the source filter.

#### Scenario: Agent chats in this workspace
- **WHEN** This workspace and Cursor-CLI are both active
- **THEN** the list includes only agent chats whose workspace path is the launch directory

#### Scenario: Workspace key keeps the source
- **WHEN** the user presses left or right
- **THEN** the workspace scope changes and the source filter stays as it was

### Requirement: Source argument
`--source` SHALL accept `cursor-cli` and `cursor-ide`. Repeating `--source` SHALL allow each named source. Omitting `--source` SHALL allow every source. The picker SHALL open on that filter.

#### Scenario: Cursor CLI flag
- **WHEN** the user passes `--source cursor-cli`
- **THEN** the picker opens with Cursor-CLI active

#### Scenario: Both source flags
- **WHEN** the user passes `--source cursor-cli` and `--source cursor-ide`
- **THEN** the list includes agent chats and IDE transcripts

#### Scenario: Flag still cycles
- **WHEN** the picker opened with `--source cursor-cli` and the user presses `s`
- **THEN** the filter moves to Cursor-IDE

### Requirement: Unknown source argument
An unknown `--source` value SHALL be rejected before the catalog is read, and the CLI SHALL write no file.

#### Scenario: Unknown value
- **WHEN** the user passes `--source other`
- **THEN** the CLI rejects the value, does not read the catalog, and writes no file

### Requirement: Filtered chat id
An id whose source is outside the `--source` filter SHALL be reported as not found, and the CLI SHALL write no file.

#### Scenario: Agent chat excluded
- **WHEN** the user passes an agent chat id and `--source cursor-ide`
- **THEN** the CLI reports that the chat was not found and writes no file

### Requirement: Empty filtered list
When the active filters leave no sessions, the picker SHALL show an empty list. Enter SHALL write no file.

#### Scenario: Enter on an empty filter
- **WHEN** the visible list is empty and the user presses Enter
- **THEN** the CLI writes no file
