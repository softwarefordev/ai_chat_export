# Spec Delta

## MODIFIED Requirements

### Requirement: Picker columns
The picker SHALL show each session's title, workspace folder name, source, and last-updated time in four columns on one row. The source column SHALL sit between the workspace and the time, SHALL be three characters wide, and SHALL read `CLI` for an agent chat and `IDE` for an IDE transcript. Rows on the same page SHALL share the same column starts. The selected row SHALL keep a `>` marker. Rules SHALL separate the header from the rows and the rows from the footer.

#### Scenario: Columns line up
- **WHEN** the page shows two sessions whose titles have different lengths
- **THEN** their workspace names start at the same column, their source cells start at the same column, and their times start at the same column

#### Scenario: Selected row
- **WHEN** a session is selected
- **THEN** that row begins with `>` and the other rows do not

#### Scenario: Source cells
- **WHEN** the page shows an agent chat and an IDE transcript
- **THEN** the agent chat's source cell is `CLI` and the transcript's source cell is `IDE`

## ADDED Requirements

### Requirement: Combined session list
The picker SHALL show agent chats and IDE transcripts in one list, newest first.

#### Scenario: Newer transcript above an older chat
- **WHEN** an IDE transcript's file time is later than an agent chat's updated time
- **THEN** the IDE row appears above that agent chat

### Requirement: IDE transcripts in the catalog
The catalog SHALL include each file at `<projects-root>/<project>/agent-transcripts/<id>/<id>.jsonl`. The projects root SHALL default to `~/.cursor/projects`. `--projects-root` SHALL replace that default. A missing projects root SHALL add no IDE rows and SHALL NOT fail the command.

#### Scenario: Transcript beside an agent chat
- **WHEN** the projects root has one transcript and the chat catalog has a different chat
- **THEN** the list contains both

#### Scenario: Missing projects root
- **WHEN** the projects root does not exist
- **THEN** the list still contains the agent chats and the command does not fail because that root is missing

#### Scenario: Custom projects root
- **WHEN** the user passes `--projects-root`
- **THEN** IDE rows come from that directory

### Requirement: Shared session listed once
An id that exists as an agent chat and as an IDE transcript SHALL appear once, from the agent chat, with source `CLI`.

#### Scenario: Same id in both stores
- **WHEN** the same id is in the chat catalog and in an IDE transcript
- **THEN** the list has one row for that id and its source cell is `CLI`

### Requirement: IDE title and time
An IDE row's title SHALL be the first line of its first user query. An empty first line SHALL use the transcript id. The row's time SHALL be that JSONL file's modification time in the local timezone, in the same form as an agent chat.

#### Scenario: Query title
- **WHEN** the first user query's first line is non-empty
- **THEN** the row title is that line

#### Scenario: Empty query
- **WHEN** the transcript has no user query text
- **THEN** the row title is the transcript id

#### Scenario: File time
- **WHEN** an IDE transcript is listed
- **THEN** the row shows that JSONL file's modification time in the catalog's local time form

### Requirement: IDE workspace
The workspace path SHALL come from `workspacePath` in the project's `.workspace-trusted` file, and the workspace column SHALL show that path's last segment. When `workspacePath` is missing, the workspace column SHALL show the project folder name and This workspace SHALL omit the row.

#### Scenario: Trusted workspace
- **WHEN** `.workspace-trusted` names a workspace path and the CLI is launched from that path
- **THEN** the row shows the last segment of that path and This workspace includes the row

#### Scenario: Missing workspace path
- **WHEN** the project has no workspace path
- **THEN** the row shows the project folder name under All chats and is absent from This workspace

### Requirement: Unreadable IDE transcript
An IDE transcript that cannot be read SHALL be omitted from the list, and the CLI SHALL warn on stderr.

#### Scenario: Unreadable file
- **WHEN** a transcript file cannot be read
- **THEN** the list omits that id and stderr names that id

### Requirement: Export an IDE transcript
The CLI SHALL export an IDE transcript by id without opening the picker, using the same HTML or Markdown output as an agent chat.

#### Scenario: IDE id
- **WHEN** the user passes the id of an IDE transcript that contains a user query
- **THEN** the CLI writes that export and does not open the picker

### Requirement: Shared id exports the agent chat
An id present in both stores SHALL export the agent chat.

#### Scenario: Shared id
- **WHEN** the user passes an id that exists in both stores
- **THEN** the export contains the agent chat's query and does not contain a query that exists only in the IDE transcript

### Requirement: Export omits the source cell
The written HTML page and Markdown file SHALL use the session title and workspace and SHALL omit the source cell.

#### Scenario: HTML header
- **WHEN** an IDE transcript is exported to HTML
- **THEN** the page shows the session title and workspace and has no source column

### Requirement: Read-only IDE transcripts
The CLI SHALL read IDE transcript files and SHALL NOT modify them or `.workspace-trusted`.

#### Scenario: Export leaves the files
- **WHEN** an IDE transcript is exported
- **THEN** the JSONL file and `.workspace-trusted` are unchanged

### Requirement: IDE conversation lines
A `user` or `assistant` line SHALL become a conversation message in transcript order. A `turn_ended` line SHALL add no section.

#### Scenario: Turn ended
- **WHEN** the transcript contains a `turn_ended` line between two assistant messages
- **THEN** those assistant messages share one Agent heading and the export has no section for `turn_ended`

### Requirement: Unrecognized IDE line
A line that is not a user message, an assistant message, or `turn_ended` SHALL be named in the footer and omitted from the body.

#### Scenario: Other line
- **WHEN** a transcript line has some other type
- **THEN** the footer names that line and the body omits it

### Requirement: IDE tool caption
A tool call in an IDE transcript SHALL use the same caption rules as an agent chat.

#### Scenario: Shell caption
- **WHEN** the user passes `--tools` and an assistant message calls a command tool with a short description
- **THEN** the caption uses that description and omits the command text
