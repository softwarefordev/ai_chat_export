# session-export Specification

## Purpose

Export AI development tool chat sessions into a documentation or demo worthy format.

## Requirements

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
The HTML page SHALL paint each User section and each Agent section with different panels. On a web theme a User panel SHALL use a warm background and a gold edge, and an Agent panel SHALL use a cooler, flatter background. On a terminal theme a User panel SHALL use a phosphor background and an amber edge, and an Agent panel SHALL use a flatter phosphor background. A System or Context section SHALL NOT use the User panel or the Agent panel.

#### Scenario: User and Agent differ
- **WHEN** the page contains a User section and an Agent section
- **THEN** those sections use different panel backgrounds

#### Scenario: Both themes keep the difference
- **WHEN** the same transcript is exported in `dark-web` and in `light-web`
- **THEN** each file paints the User panel and the Agent panel differently, and the User panel keeps its gold edge

#### Scenario: Terminal themes keep the difference
- **WHEN** the same transcript is exported in `terminal-dark` and in `terminal-light`
- **THEN** each file paints the User panel and the Agent panel differently, and the User panel keeps its amber edge

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
The navigator time SHALL be 10px. On a web theme the navigator SHALL use a sans-serif face and the transcript SHALL keep its serif face. On a terminal theme the navigator and the transcript SHALL use a monospace face.

#### Scenario: Time is 10px
- **WHEN** the navigator shows a turn time
- **THEN** that time is 10px

#### Scenario: Navigator face
- **WHEN** a web theme page is written
- **THEN** the navigator uses a sans-serif face and the transcript keeps its serif face

#### Scenario: Terminal face
- **WHEN** a terminal theme page is written
- **THEN** the navigator and the transcript use a monospace face

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

### Requirement: Chat catalog
The CLI SHALL list each local agent chat with its title, the workspace folder name, and the last-updated time in the local timezone.

#### Scenario: Chat with a title
- **WHEN** the local chat store has a chat with a title, a workspace path, and an updated time
- **THEN** the list shows that title, the last segment of the workspace path, and that updated time

#### Scenario: Chat without a title
- **WHEN** a chat has no title
- **THEN** the list shows the chat id in place of a title

### Requirement: List scope
The CLI SHALL provide All chats and This workspace. This workspace SHALL include only chats whose workspace path is the directory the CLI was launched from.

#### Scenario: All chats
- **WHEN** All chats is selected
- **THEN** the list includes every catalogued chat

#### Scenario: This workspace
- **WHEN** This workspace is selected
- **THEN** the list includes only chats whose workspace path is the launch directory

### Requirement: Interactive picker
Running the CLI without a chat id SHALL open a picker. Up and down SHALL move the selection, left and right SHALL switch scope, Enter SHALL open a file-name line for the selected chat and SHALL NOT write a file yet, and Esc SHALL close the picker without writing files. The name line SHALL start as the title file name, or the chat id when the chat has no title. Confirming that line SHALL write the export under that file name in the output directory. A stem that is `CON`, `PRN`, `AUX`, `NUL`, `COM1` through `COM9`, or `LPT1` through `LPT9`, compared without regard to case, SHALL be replaced with the chat id, or with the id plus `-export` when the id is also one of those names. The replacement applies to the name line's starting value and to the name confirmed from the line.

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

#### Scenario: Reserved default name
- **WHEN** the selected chat's title is `CON` and the user opens the name line
- **THEN** the name line shows the chat id with the export extension and does not show `CON.html`

#### Scenario: Reserved confirmed draft
- **WHEN** the user sets the name line to `COM1` and presses Enter
- **THEN** the written file uses the chat id as its stem and is not named `COM1.html`

### Requirement: Picker leaves chats intact
The picker SHALL NOT delete or modify chats in the local store.

#### Scenario: Backspace in the picker
- **WHEN** the user presses Backspace while the picker is open
- **THEN** the selected chat remains in the store

### Requirement: Theme shown before export
The picker SHALL show the HTML theme that Enter will write.

#### Scenario: Default theme is visible
- **WHEN** the picker opens without a theme request
- **THEN** the picker shows `terminal-dark` as the theme that will be written

#### Scenario: Light theme is visible
- **WHEN** the user requested `terminal-light` and the picker is open
- **THEN** the picker shows `terminal-light` as the theme that will be written

#### Scenario: Web theme is visible
- **WHEN** the user requested `dark-web` or `light-web` and the picker is open
- **THEN** the picker shows that requested name as the theme that will be written

### Requirement: Export by chat id
The CLI SHALL export a chat by id without opening the picker.

#### Scenario: Known id
- **WHEN** the user passes the id of a chat that has a conversation
- **THEN** the CLI writes that chat's HTML and Markdown exports and does not open the picker

#### Scenario: Unknown id
- **WHEN** the user passes a chat id that is not in the catalog
- **THEN** the CLI reports that the chat was not found and writes no files

### Requirement: Paired HTML and Markdown
A successful export SHALL write one HTML file from the filtered transcript and SHALL print that path. Passing `--markdown` SHALL also write one Markdown file from that same transcript and SHALL print both paths.

#### Scenario: HTML by default
- **WHEN** a chat with a conversation is exported without `--markdown` into a directory that has no Markdown file
- **THEN** the HTML file exists, the CLI prints its path, and no Markdown file exists

#### Scenario: Markdown when requested
- **WHEN** the user passes `--markdown`
- **THEN** the HTML file and the Markdown file exist and the CLI prints both paths

### Requirement: Output location and names
The CLI SHALL name each file it writes from the chat title and write it in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. A default export SHALL write the HTML file. Passing `--markdown` SHALL also write the Markdown file. Passing `--name` without an output directory SHALL write only that path. Without a chat id, `--name` SHALL write no file. When a file this export writes already exists, the export SHALL replace that file. A generated stem that is `CON`, `PRN`, `AUX`, `NUL`, `COM1` through `COM9`, or `LPT1` through `LPT9`, compared without regard to case, SHALL use the chat id instead. When that id is also one of those names, the stem SHALL be the id plus `-export`. A path passed to `--name` SHALL be written as given.

#### Scenario: Default directory
- **WHEN** the user does not supply an output directory and does not pass `--name`
- **THEN** the HTML file is created in the current directory

#### Scenario: Supplied directory
- **WHEN** the user supplies an output directory and does not pass `--markdown` and does not pass `--name`
- **THEN** the HTML file is created in that directory

#### Scenario: Existing HTML file
- **WHEN** the HTML target already exists and the user does not pass `--markdown` and does not pass `--name`
- **THEN** the CLI replaces the HTML file, prints its path, and exits successfully

#### Scenario: Existing Markdown file
- **WHEN** a Markdown file is already present and the user does not pass `--markdown` and does not pass `--name`
- **THEN** that Markdown file is unchanged

#### Scenario: Markdown beside HTML
- **WHEN** the user passes `--markdown` and does not pass `--name` and either target file already exists
- **THEN** the CLI replaces the existing target files, writes any missing target, prints both paths, and exits successfully

#### Scenario: Neighboring file
- **WHEN** the output directory contains a file that is not a target of this export
- **THEN** that file is unchanged

#### Scenario: Name without a chat id
- **WHEN** the user passes `--name` and does not pass a chat id
- **THEN** the CLI reports the error, does not open the picker, and writes no file

#### Scenario: Named path
- **WHEN** the user passes a chat id and `--name` with a file path and does not pass `--markdown` or an output directory
- **THEN** the CLI writes the HTML export to that path, prints that path, does not create a title-named file, and does not open the picker

#### Scenario: Named path by chat id
- **WHEN** the user passes a chat id and `--name` with a file path and does not pass `--markdown` or an output directory
- **THEN** the CLI writes the HTML export to that path, prints that path, and does not open the picker

#### Scenario: Named Markdown path
- **WHEN** the user passes a chat id, `--name`, and `--markdown` and does not pass an output directory
- **THEN** the CLI writes the Markdown export to that path, prints that path, and does not write a second file

#### Scenario: Name and output directory
- **WHEN** the user passes a chat id, `--name`, and an output directory
- **THEN** the CLI reports the conflict, writes no file, does not open the picker, and exits unsuccessfully

#### Scenario: Relative named path
- **WHEN** the user passes a chat id and `--name` with a relative file path and does not pass an output directory
- **THEN** that file is created relative to the current directory

#### Scenario: Existing named file
- **WHEN** the user passes a chat id and the path passed to `--name` already exists and the user does not pass an output directory
- **THEN** the CLI replaces that file, prints its path, and exits successfully

#### Scenario: Missing parent directory
- **WHEN** the user passes a chat id and the parent directory of the `--name` path does not exist and the user does not pass an output directory
- **THEN** the CLI creates that directory and writes the file there

#### Scenario: Name is a directory
- **WHEN** the user passes a chat id and the path passed to `--name` is an existing directory
- **THEN** the CLI reports the error, writes no file, and exits unsuccessfully

#### Scenario: Reserved title
- **WHEN** the chat title is `CON` and the user exports without `--name`
- **THEN** the written file uses the chat id as its stem and is not named `CON.html`

#### Scenario: Reserved markdown title
- **WHEN** the chat title is `nul` and the user passes `--markdown` and does not pass `--name`
- **THEN** the written file uses the chat id as its stem and is not named `nul.md`

#### Scenario: Reserved id
- **WHEN** the chat has no title, its id is `CON`, and the user exports without `--name`
- **THEN** the written stem is `CON-export`

#### Scenario: Explicit reserved path
- **WHEN** the user passes a chat id and `--name` whose file name is `CON.html`
- **THEN** the CLI writes that path

### Requirement: Default transcript
The default transcript SHALL include each user query and the assistant's visible text, in conversation order. The query SHALL be the inner text of each `user_query` element. When the typed text has no `user_query` element and no wrapper elements, that typed text SHALL be the query. It SHALL omit a conversation summary, Cursor command blocks, other injected context, timestamp markup, tool captions, system text, assistant reasoning, and raw tool output.

#### Scenario: Typed prompt beside injected context
- **WHEN** a user turn contains a query element and injected context
- **THEN** the default transcript includes the query text and omits the injected context

#### Scenario: Query inside markup
- **WHEN** a user turn's typed text wraps the query in a `user_query` element and also contains a timestamp element
- **THEN** the default transcript includes the inner query text and omits the tags and the timestamp element

#### Scenario: Plain prompt
- **WHEN** the typed text has no wrapper elements
- **THEN** that text is the User section

#### Scenario: Summary only
- **WHEN** a user message contains only a `conversation_summary` element
- **THEN** the default transcript has no User section for that message

#### Scenario: Tool call omitted
- **WHEN** the user exports without `--tools` and without `--verbose`, and a turn contains a tool call and a tool result
- **THEN** the transcript omits the caption and the raw result

### Requirement: Agent stretch
Consecutive assistant messages, up to the next typed user prompt, SHALL appear under a single Agent heading in HTML and Markdown. A stretch with no visible assistant text and no visible tool captions SHALL produce no Agent heading.

#### Scenario: Several assistant messages
- **WHEN** two assistant messages occur before the next typed user prompt
- **THEN** the export contains one Agent heading covering both messages

#### Scenario: Next prompt starts a new stretch
- **WHEN** a typed user prompt follows an assistant message and another assistant message follows that prompt
- **THEN** the export contains two Agent headings

#### Scenario: Tools only
- **WHEN** an agent stretch contains only tool calls and the export does not show tool captions
- **THEN** the export has no Agent heading for that stretch

### Requirement: Optional tool captions
The CLI SHALL omit tool captions unless the user passes `--tools` or `--verbose`. Shown captions SHALL sit inside the Agent section, in conversation order, among the assistant paragraphs they belong to.

#### Scenario: Tools flag shows a caption
- **WHEN** the user passes `--tools` and a turn contains a tool call and a tool result
- **THEN** the transcript includes one caption for the call and omits the raw result

#### Scenario: Verbose shows captions
- **WHEN** the user passes `--verbose` and a turn contains a tool call
- **THEN** the transcript includes that call's caption

### Requirement: Tool caption
A tool caption SHALL identify the tool with a short label: the file path for a file read, the pattern for a file search, or the short description recorded with a command. The caption SHALL omit the full command text.

#### Scenario: Command caption
- **WHEN** a tool caption is included for a command that has a short description
- **THEN** the caption uses that description and omits the command text

#### Scenario: File read caption
- **WHEN** a tool caption is included for a file read
- **THEN** the caption includes the file path

### Requirement: Verbose transcript
Verbose mode SHALL add system text, injected context, assistant reasoning, raw tool output, and tool captions, in conversation order. Additions that belong to an agent stretch SHALL stay inside that stretch's Agent heading. Verbose mode SHALL NOT, by itself, add a conversation summary or a Cursor command block to the User section.

#### Scenario: Verbose includes a tool result
- **WHEN** the user exports with verbose mode and a turn has a tool result
- **THEN** the transcript includes that raw tool output inside the Agent heading

#### Scenario: Verbose keeps one Agent heading
- **WHEN** verbose mode exports two assistant messages and a tool result before the next typed prompt
- **THEN** one Agent heading contains both messages, the caption, and the tool result

#### Scenario: Verbose without detail
- **WHEN** the user exports with verbose mode and without `--detail`, and a user turn has a Cursor command block, a conversation summary, and other injected context
- **THEN** the transcript includes the other injected context and does not add the command block or the summary to the User section

### Requirement: HTML theme chosen at export
The HTML file SHALL use `terminal-dark` unless the user requests `terminal-light`, `dark-web`, or `light-web`. The requested theme SHALL be part of the written file. `dark-web` SHALL keep the former dark palette. `light-web` SHALL keep the former light palette. The names `dark` and `light` SHALL be rejected.

#### Scenario: Dark by default
- **WHEN** the user exports without requesting a theme
- **THEN** the HTML file renders in `terminal-dark`

#### Scenario: Light when requested
- **WHEN** the user requests `terminal-light`
- **THEN** the HTML file renders in `terminal-light`

#### Scenario: Web dark when requested
- **WHEN** the user requests `dark-web`
- **THEN** the HTML file renders in the former dark palette

#### Scenario: Web light when requested
- **WHEN** the user requests `light-web`
- **THEN** the HTML file renders in the former light palette

#### Scenario: Former names are rejected
- **WHEN** the user passes `dark` or `light` as the theme
- **THEN** the CLI rejects the request and writes no file

### Requirement: Terminal page shape
A terminal theme SHALL use square section corners. A web theme SHALL keep rounded section corners.

#### Scenario: Terminal corners
- **WHEN** the page uses `terminal-dark` or `terminal-light`
- **THEN** the sections have square corners

#### Scenario: Web corners
- **WHEN** the page uses `dark-web` or `light-web`
- **THEN** the sections keep rounded corners

### Requirement: Self-contained original page
The HTML file SHALL render its transcript and styling with no external assets. The page SHALL use an original visual design and SHALL NOT embed Cursor's logo or proprietary stylesheet.

#### Scenario: Opened with no network
- **WHEN** the HTML file is opened without network access
- **THEN** the transcript and its styling render from that file

### Requirement: Markdown has no theme
The Markdown file SHALL contain the same prompts, assistant text, and shown tool captions as the HTML file for that export. It SHALL NOT encode a color theme.

#### Scenario: Matching turns
- **WHEN** the user passes `--markdown`
- **THEN** the Markdown file contains the same visible turns as the HTML file and does not encode a color theme

### Requirement: Read-only chat store
The CLI SHALL read the local chat store and SHALL NOT modify it.

#### Scenario: Export does not change the store
- **WHEN** an export finishes
- **THEN** the chat store's files are unchanged

### Requirement: Store path stays read-only
The CLI SHALL open the chat database at its given path in read-only mode. A `?` or `#` in that path SHALL remain part of the path and SHALL NOT select another open mode. The database file SHALL be unchanged.

#### Scenario: Question mark in the path
- **WHEN** the database path contains `?`
- **THEN** the CLI reads that path read-only and does not create or change a database at the path truncated at `?`

#### Scenario: Hash in the path
- **WHEN** the database path contains `#`
- **THEN** the CLI reads that path read-only and does not create or change a database at the path truncated at `#`

### Requirement: Chat with no conversation
The CLI SHALL report when a selected chat has no conversation, and SHALL write no export files for it.

#### Scenario: Metadata only
- **WHEN** the user exports a chat that has catalog metadata and no conversation
- **THEN** the CLI reports that the chat has no transcript and writes no files

### Requirement: Unrecognized conversation data
The export SHALL include the turns the reader understands and SHALL name skipped conversation data in a short footer.

#### Scenario: Unknown blob
- **WHEN** the conversation contains data the reader cannot interpret
- **THEN** the export includes the understood turns and a footer entry for the skipped data

### Requirement: Image not attached to a turn
The export SHALL name a stored image that is not part of a visible turn in the footer, and SHALL omit that image from the body.

#### Scenario: Unlinked image
- **WHEN** the conversation stores an image that is not part of a visible turn
- **THEN** the footer names the image and the body does not embed it

### Requirement: Safe embedded image
The HTML page SHALL embed an image only when its media type is `image/png`, `image/jpeg`, `image/gif`, or `image/webp` and its payload is base64. Media type `image/jpg` SHALL be embedded as `image/jpeg`. Any other image SHALL be omitted from the image tag. The page SHALL contain no script.

#### Scenario: PNG stays embedded
- **WHEN** a turn includes an image of type `image/png` whose payload is base64
- **THEN** the page shows that image and contains no script element

#### Scenario: JPEG alias
- **WHEN** a turn includes an image of type `image/jpg` whose payload is base64
- **THEN** the page embeds that image as `image/jpeg`

#### Scenario: Markup in the payload
- **WHEN** an image payload contains a quote followed by a script element
- **THEN** the page contains no script element and does not treat that payload as markup

#### Scenario: SVG is omitted
- **WHEN** an image media type is `image/svg+xml`
- **THEN** the page does not embed that payload

#### Scenario: HTML media type is omitted
- **WHEN** an image media type is `text/html`
- **THEN** the page does not embed that payload and contains no script element

### Requirement: User turn detail
The CLI SHALL omit conversation summaries and Cursor command blocks unless the user passes `--detail`. A shown summary SHALL be the inner text of each `conversation_summary` element. A shown command block SHALL be the inner text of each `cursor_commands` element. Shown blocks SHALL appear once inside that User section, after the query when a query is present.

#### Scenario: Detail shows the command
- **WHEN** the user passes `--detail` and a user turn contains a `cursor_commands` element and a query
- **THEN** the User section includes that element's inner text after the query

#### Scenario: Detail shows the summary
- **WHEN** the user passes `--detail` and a user message contains a `conversation_summary` element and a query
- **THEN** the User section includes that element's inner text after the query

#### Scenario: Summary only with detail
- **WHEN** the user passes `--detail` and a user message contains only a `conversation_summary` element
- **THEN** the transcript has a User section whose text is that element's inner text

#### Scenario: Detail without extras
- **WHEN** the user passes `--detail` and a user turn has no `conversation_summary` element and no `cursor_commands` element
- **THEN** the User section contains the query and no summary or command block

#### Scenario: Both flags show each block once
- **WHEN** the user passes `--detail` and `--verbose` and a user turn contains a summary and a command block inside injected context
- **THEN** each block appears once, in the User section, and the injected context does not repeat either block

### Requirement: Turn timestamp
Each visible User section and each Agent section SHALL show a formatted timestamp in the catalog style: abbreviated month, day, year, and 12-hour time. A User section SHALL use the timestamp recorded on that user turn. An Agent section SHALL use the timestamp of the user turn that opened that stretch. A section with no recorded turn timestamp SHALL omit the time. The chat header timestamp SHALL remain.

#### Scenario: User turn time
- **WHEN** a visible user turn records `Friday, Oct 23, 2026, 11:13 AM (UTC-7)`
- **THEN** the User section shows `Oct 23, 2026 11:13 AM`

#### Scenario: Agent stretch time
- **WHEN** an Agent section follows a user turn with that timestamp
- **THEN** the Agent section shows the same formatted time

#### Scenario: Missing turn time
- **WHEN** a visible section has no recorded turn timestamp
- **THEN** that section omits the time and the chat header still shows the chat's updated time

#### Scenario: Both outputs
- **WHEN** the user exports HTML and Markdown for a turn that has a timestamp
- **THEN** both files show that turn's formatted time

### Requirement: User heading
HTML and Markdown SHALL label each user section User. An agent section SHALL stay labeled Agent.

#### Scenario: User query heading
- **WHEN** a user query is exported to HTML and Markdown
- **THEN** the HTML heading is User and the Markdown heading is User

#### Scenario: Agent heading unchanged
- **WHEN** an agent stretch is exported
- **THEN** its heading is Agent

### Requirement: Navigator time format
A parsed navigator turn time SHALL be written as YY-MM-DD hh:mm with a two-digit year, zero-padded month and day, and a 24-hour clock. An unparsed turn time SHALL stay as stored. User and Agent headings SHALL keep their existing turn time.

#### Scenario: Afternoon becomes 24-hour
- **WHEN** a User section's turn time is `Oct 23, 2026 01:08 PM`
- **THEN** the navigator shows `26-10-23 13:08`

#### Scenario: Morning stays in the morning
- **WHEN** a User section's turn time is `Oct 23, 2026 11:13 AM`
- **THEN** the navigator shows `26-10-23 11:13`

#### Scenario: Single-digit day is zero-padded
- **WHEN** a User section's turn time is `Sep 1, 2026 09:05 AM`
- **THEN** the navigator shows `26-09-01 09:05`

#### Scenario: Midnight is zero hour
- **WHEN** a User section's turn time is `Oct 23, 2026 12:00 AM`
- **THEN** the navigator shows `26-10-23 00:00`

#### Scenario: Noon stays at twelve
- **WHEN** a User section's turn time is `Oct 23, 2026 12:00 PM`
- **THEN** the navigator shows `26-10-23 12:00`

#### Scenario: Unparsed time stays as stored
- **WHEN** a User section's turn time cannot be parsed
- **THEN** the navigator shows that text as stored

#### Scenario: Heading keeps the catalog time
- **WHEN** the same turn appears in a User heading and in the navigator
- **THEN** the heading keeps the catalog time and the navigator shows the compact time

### Requirement: Navigator time size
A navigator turn time SHALL use a smaller font than the query text in that entry.

#### Scenario: Parsed time is smaller
- **WHEN** the navigator shows a parsed turn time beside a query
- **THEN** that time uses a smaller font than the query text

#### Scenario: Unparsed time is smaller
- **WHEN** the navigator shows an unparsed turn time beside a query
- **THEN** that time uses the same smaller font

### Requirement: Name line stays on the list
While the file-name line is open, the picker SHALL keep the chat list, the selected row, and the theme on the same screen. The name line SHALL say that typing edits the name. A draft longer than the picker width SHALL show its end, and the chat columns SHALL stay aligned. Up and down SHALL leave the selected chat unchanged while the name line is open.

#### Scenario: Long file name
- **WHEN** the draft is longer than the picker width
- **THEN** the name line shows the end of the draft, leaves its last column for the cursor, and the chat columns stay aligned

#### Scenario: Movement while naming
- **WHEN** the user presses up or down while the name line is open
- **THEN** the selected chat stays the same and the list remains on screen

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

### Requirement: Turn filter
Each User navigator entry SHALL have a checkbox beside its fragment link. No checkbox SHALL start checked. With none checked, every transcript section SHALL stay visible. The page SHALL still contain no script.

#### Scenario: Nothing starts checked
- **WHEN** the page opens
- **THEN** every checkbox is unchecked and every User section and Agent section is visible

#### Scenario: Checkbox beside the link
- **WHEN** a User entry is shown
- **THEN** a checkbox sits beside that entry's fragment link and the link remains

### Requirement: Filtered turns
While one or more navigator checkboxes are checked, the transcript SHALL show those User sections and the Agent sections that follow each of them until the next User section. Other User, Agent, System, and Context sections SHALL be hidden. The chat title, the footer, and every navigator entry SHALL stay visible.

#### Scenario: One selected turn
- **WHEN** the reader checks the first of three User entries and an Agent section follows that User section
- **THEN** that User section and that Agent section are visible and the other User sections are hidden

#### Scenario: Two selected turns
- **WHEN** the reader checks the first and third User entries
- **THEN** both of those User sections and the Agent sections that follow each of them are visible and the second User section is hidden

#### Scenario: System and context stay out
- **WHEN** a checkbox is checked and the page has a System section or a Context section
- **THEN** that section is hidden

#### Scenario: Title and navigator stay
- **WHEN** a checkbox is checked
- **THEN** the chat title, the footer, and every navigator entry remain visible

### Requirement: Clear filter
The navigator SHALL offer Clear filter pinned above the turn list and again after the last turn. Both controls SHALL appear only while a checkbox is checked. Using either SHALL clear every checkbox and show every transcript section again.

#### Scenario: Both ends
- **WHEN** a checkbox is checked
- **THEN** Clear filter is shown pinned above the turn list and again after the last turn

#### Scenario: Hidden when nothing is checked
- **WHEN** no checkbox is checked
- **THEN** Clear filter is not shown

#### Scenario: Either control restores the transcript
- **WHEN** the reader uses either Clear filter
- **THEN** every checkbox is unchecked and every transcript section is visible

### Requirement: Navigator time grouping
The space between a navigator turn time and the prompt under it SHALL be smaller than the space between navigator entries. An entry with no turn time SHALL use that same space between entries. The first entry SHALL have no added space above it.

#### Scenario: Time sits with the prompt below
- **WHEN** the navigator shows two entries that each have a turn time and a prompt
- **THEN** the space between each time and its prompt is smaller than the space between the two entries

#### Scenario: Untimed entry keeps the row gap
- **WHEN** an entry has no turn time and another entry follows it
- **THEN** the space between those entries matches the space between two timed entries

#### Scenario: First entry stays at the top
- **WHEN** the navigator shows more than one entry
- **THEN** the first entry has no added space above it

### Requirement: Combined session list
The picker SHALL show agent chats, IDE transcripts, Copilot CLI sessions, and Copilot IDE sessions in one list, newest first.

#### Scenario: Newer transcript above an older chat
- **WHEN** an IDE transcript's file time is later than an agent chat's updated time
- **THEN** the IDE row appears above that agent chat

#### Scenario: Newer Copilot session above an older chat
- **WHEN** a Copilot CLI session's updated time is later than an agent chat's updated time
- **THEN** the Copilot row appears above that agent chat

#### Scenario: Newer Copilot IDE session above an older chat
- **WHEN** a Copilot IDE session's updated time is later than an agent chat's updated time
- **THEN** the Copilot IDE row appears above that agent chat

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
An id that exists as an agent chat and as an IDE transcript SHALL appear once, from the agent chat, with source `Cu-CLI`.

#### Scenario: Same id in both stores
- **WHEN** the same id is in the chat catalog and in an IDE transcript
- **THEN** the list has one row for that id and its source cell is `Cu-CLI`

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

### Requirement: Source filter line
The picker SHALL show a source line under the workspace scope. The line SHALL name All sources, Cursor-CLI, Cursor-IDE, Copilot-CLI, and Copilot-IDE. It SHALL mark All sources when every source is allowed, and SHALL mark each allowed source when the filter is a subset.

#### Scenario: Open on every source
- **WHEN** the picker opens without `--source`
- **THEN** the source line marks All sources

#### Scenario: One source is marked
- **WHEN** the active filter allows only agent chats
- **THEN** the source line marks Cursor-CLI and does not mark All sources

#### Scenario: Copilot CLI is marked
- **WHEN** the active filter allows only Copilot CLI sessions
- **THEN** the source line marks Copilot-CLI and does not mark All sources

#### Scenario: Copilot IDE is marked
- **WHEN** the active filter allows only Copilot IDE sessions
- **THEN** the source line marks Copilot-IDE and does not mark All sources

### Requirement: Source filter key
Pressing `s` on the chat list, in either case, SHALL cycle the filter through All sources, Cursor-CLI, Cursor-IDE, Copilot-CLI, and Copilot-IDE, then back to All sources. The selection SHALL return to the first visible row. The footer SHALL name `s`.

#### Scenario: Cycle to Cursor-CLI
- **WHEN** All sources is active and the user presses `s`
- **THEN** Cursor-CLI is active and the first visible row is selected

#### Scenario: Cycle to Copilot-CLI
- **WHEN** Cursor-IDE is active and the user presses `s`
- **THEN** Copilot-CLI is active and the first visible row is selected

#### Scenario: Cycle to Copilot-IDE
- **WHEN** Copilot-CLI is active and the user presses `s`
- **THEN** Copilot-IDE is active and the first visible row is selected

#### Scenario: Cycle back to All sources
- **WHEN** Copilot-IDE is active and the user presses `s`
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
`--source` SHALL accept `cursor-cli`, `cursor-ide`, `copilot-cli`, and `copilot-ide`. Repeating `--source` SHALL allow each named source. Omitting `--source` SHALL allow every source. The picker SHALL open on that filter.

#### Scenario: Cursor CLI flag
- **WHEN** the user passes `--source cursor-cli`
- **THEN** the picker opens with Cursor-CLI active

#### Scenario: Both source flags
- **WHEN** the user passes `--source cursor-cli` and `--source cursor-ide`
- **THEN** the list includes agent chats and IDE transcripts and omits Copilot CLI sessions and Copilot IDE sessions

#### Scenario: Flag still cycles
- **WHEN** the picker opened with `--source cursor-cli` and the user presses `s`
- **THEN** the filter moves to Cursor-IDE

#### Scenario: Copilot CLI flag
- **WHEN** the user passes `--source copilot-cli`
- **THEN** the picker opens with Copilot-CLI active

#### Scenario: Copilot IDE flag
- **WHEN** the user passes `--source copilot-ide`
- **THEN** the picker opens with Copilot-IDE active

#### Scenario: Partial flags return to All sources
- **WHEN** the picker opened with `--source cursor-cli` and `--source cursor-ide` and the user presses `s`
- **THEN** the filter moves to All sources

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

### Requirement: Copilot source cell
A Copilot CLI row's source cell SHALL be `Cp-CLI` in the six-character source column.

#### Scenario: Copilot source cell
- **WHEN** the page shows a Copilot CLI session
- **THEN** that row's source cell is `Cp-CLI`

### Requirement: Copilot CLI sessions in the catalog
The catalog SHALL include each session recorded in `<copilot-root>/session-store.db`. The copilot root SHALL default to `~/.copilot`. `--copilot-root` SHALL replace that default. A missing copilot root SHALL add no Copilot rows and SHALL NOT fail the command. A session directory that is absent from that database SHALL stay out of the list.

#### Scenario: Session beside an agent chat
- **WHEN** the copilot root has one session and the chat catalog has a different chat
- **THEN** the list contains both

#### Scenario: Missing copilot root
- **WHEN** the copilot root does not exist
- **THEN** the list still contains the agent chats and the command does not fail because that root is missing

#### Scenario: Custom copilot root
- **WHEN** the user passes `--copilot-root`
- **THEN** Copilot rows come from that directory

#### Scenario: Directory without a database session
- **WHEN** a session-state directory has no row in the session database
- **THEN** the list omits that directory

### Requirement: Copilot session listed beside a Cursor id
An id that exists as a Copilot CLI session and as a Cursor agent chat or IDE transcript SHALL appear as both rows.

#### Scenario: Same id in Copilot and the chat store
- **WHEN** the same id is a Copilot CLI session and an agent chat
- **THEN** the list has both rows and the Copilot row's source cell is `Cp-CLI`

### Requirement: Copilot title
A Copilot row's title SHALL be the session summary. An empty summary SHALL use the first line of the first user message. When that line is empty, the title SHALL be the session id.

#### Scenario: Summary title
- **WHEN** the session summary is non-empty
- **THEN** the row title is that summary

#### Scenario: Empty summary
- **WHEN** the summary is empty and the first user message's first line is non-empty
- **THEN** the row title is that line

#### Scenario: No title text
- **WHEN** the summary and the user messages are empty
- **THEN** the row title is the session id

### Requirement: Copilot list time
A Copilot row's time SHALL be the session's updated time, interpreted as UTC and shown in the catalog's local time form. An unparsed updated time SHALL be shown as stored, with whitespace collapsed.

#### Scenario: Updated time
- **WHEN** a Copilot session has an updated time
- **THEN** the row shows that time in the catalog's local time form

### Requirement: Copilot workspace
The workspace column SHALL show the last segment of the session's working directory. When that directory is missing, the column SHALL be empty and This workspace SHALL omit the row.

#### Scenario: Working directory
- **WHEN** the session has a working directory and the CLI is launched from that path
- **THEN** the row shows the last segment of that path and This workspace includes the row

#### Scenario: Missing working directory
- **WHEN** the session has no working directory
- **THEN** the workspace column is empty and This workspace omits the row

### Requirement: Export a Copilot session
Passing the id of a Copilot CLI session SHALL write that session through the same HTML or Markdown export as an agent chat. The written page SHALL omit the source cell.

#### Scenario: HTML export
- **WHEN** the user passes a Copilot session id
- **THEN** the export contains the user message and the assistant text and omits the source cell

### Requirement: Copilot turn text
The default Copilot transcript SHALL show each turn's user message and assistant text. Consecutive assistant text SHALL share one Agent heading until the next user message. An empty assistant reply SHALL add no Agent heading.

#### Scenario: User and assistant
- **WHEN** a turn has a user message and assistant text
- **THEN** the export shows that user message and that assistant text under one Agent heading

#### Scenario: Empty assistant
- **WHEN** a turn has a user message and no assistant text
- **THEN** the export shows the user message and no Agent heading for that turn

### Requirement: Copilot session with no turns
A Copilot session with no user message and no assistant text SHALL be reported with `Chat has no transcript: {id}`, and the CLI SHALL write no file.

#### Scenario: Empty session
- **WHEN** the user passes the id of a Copilot session that has no turns
- **THEN** the CLI reports that the chat has no transcript and writes no file

### Requirement: Copilot tool caption
With `--tools`, a Copilot tool call SHALL show one caption and SHALL omit the tool result.

#### Scenario: Read a file
- **WHEN** the user passes `--tools` and the tool is `view` with a path
- **THEN** the caption is `Read` plus that path and the result is omitted

#### Scenario: Find files
- **WHEN** the user passes `--tools` and the tool is `glob` with a pattern
- **THEN** the caption is `Glob` plus that pattern and the result is omitted

#### Scenario: Run a command
- **WHEN** the user passes `--tools` and the tool is `powershell` with a description
- **THEN** the caption is `Ran` plus that description and the command text is omitted

#### Scenario: Search files
- **WHEN** the user passes `--tools` and the tool is `grep` with a pattern
- **THEN** the caption is `Grep` plus that pattern and the result is omitted

#### Scenario: Create a file
- **WHEN** the user passes `--tools` and the tool is `create` with a path
- **THEN** the caption is `Create` plus that path and the result is omitted

### Requirement: Copilot verbose detail
`--verbose` SHALL include Copilot tool captions, system message text, reasoning text, and tool results.

#### Scenario: Reasoning and result
- **WHEN** the user passes `--verbose` and a turn has reasoning text and a tool result
- **THEN** the export includes that reasoning text and that tool result

#### Scenario: System message
- **WHEN** the user passes `--verbose` and the session has a system message
- **THEN** the export includes that system message text

### Requirement: Copilot encrypted content
Encrypted Copilot content SHALL stay out of the export, including when `--verbose` is set.

#### Scenario: Encrypted assistant content
- **WHEN** an assistant message carries encrypted content
- **THEN** the export omits that encrypted content

### Requirement: Copilot turns without an event log
When a Copilot session has turn text and no event log, the export SHALL write that turn text, and `--tools` SHALL add no captions.

#### Scenario: Missing event log
- **WHEN** the session has turns and no event log
- **THEN** the export contains the turn text and no tool caption

### Requirement: Unreadable Copilot events
An unreadable Copilot event log SHALL warn `Unreadable Copilot events {id}: {error}`, and the export SHALL still write the turn text.

#### Scenario: Event log cannot be read
- **WHEN** the event log cannot be read and the session has turn text
- **THEN** the warning names the session id and the export still contains the turn text

### Requirement: Copilot checkpoint ignored
A Copilot checkpoint index SHALL NOT become a turn and SHALL NOT add a footer line.

#### Scenario: Index file
- **WHEN** the session directory contains a checkpoint index
- **THEN** the export omits that index

### Requirement: Read-only Copilot store
The tool SHALL open the Copilot database read-only and SHALL leave the database, the event log, and the checkpoint index byte-for-byte unchanged.

#### Scenario: Bytes unchanged
- **WHEN** a Copilot session is exported
- **THEN** the database and the event log have the same bytes as before the export

### Requirement: Unreadable Copilot store
An unreadable Copilot database SHALL be omitted with the warning `Unreadable Copilot store: {error}`, and the command SHALL still list the other sessions.

#### Scenario: Database cannot be read
- **WHEN** the session database cannot be read
- **THEN** the warning names the failure and the agent chats remain in the list

### Requirement: Copilot IDE source cell
A Copilot IDE row's source cell SHALL be `Cp-IDE` in the six-character source column for a VS Code session, a Rider session, and a Visual Studio session.

#### Scenario: Copilot IDE source cell
- **WHEN** the page shows a Copilot IDE session from any of those hosts
- **THEN** that row's source cell is `Cp-IDE`

### Requirement: VS Code Copilot sessions in the catalog
The catalog SHALL include each Copilot chat session under the VS Code user directory's workspace session folders and empty-window session folder when that session has a user or assistant turn. The directory SHALL default to the platform Visual Studio Code User directory. `--vscode-root` SHALL replace that default. A missing directory SHALL add no rows and SHALL NOT fail the command.

#### Scenario: Session beside an agent chat
- **WHEN** the VS Code root has one Copilot session with a user turn and the chat catalog has a different chat
- **THEN** the list contains both

#### Scenario: Missing VS Code root
- **WHEN** the VS Code root does not exist
- **THEN** the list still contains the agent chats and the command does not fail because that root is missing

#### Scenario: Custom VS Code root
- **WHEN** the user passes `--vscode-root`
- **THEN** VS Code Copilot rows come from that directory

### Requirement: Rider Copilot sessions in the catalog
The catalog SHALL include each Copilot chat session under `<copilot-ide-root>/rd/chat-agent-sessions` when that session has a user or assistant turn. The root SHALL default to the platform local `github-copilot` directory. `--copilot-ide-root` SHALL replace that default. A missing root SHALL add no rows and SHALL NOT fail the command.

#### Scenario: Rider session beside an agent chat
- **WHEN** the Copilot IDE root has one Rider session with a user turn and the chat catalog has a different chat
- **THEN** the list contains both

#### Scenario: Missing Copilot IDE root
- **WHEN** the Copilot IDE root does not exist
- **THEN** the list still contains the agent chats and the command does not fail because that root is missing

#### Scenario: Custom Copilot IDE root
- **WHEN** the user passes `--copilot-ide-root`
- **THEN** Rider rows come from that directory

### Requirement: Visual Studio Copilot sessions in the catalog
The catalog SHALL include each Copilot chat session under `<copilot-ide-root>/vs` when that session has a user or assistant turn. A missing `vs` directory SHALL add no Visual Studio rows and SHALL NOT fail the command.

#### Scenario: Visual Studio session beside an agent chat
- **WHEN** the Copilot IDE root has one Visual Studio session with a user turn
- **THEN** the list contains that session

#### Scenario: Missing Visual Studio directory
- **WHEN** the Copilot IDE root has no `vs` directory
- **THEN** the list still contains the other sessions and the command does not fail because that directory is missing

### Requirement: Empty Copilot IDE draft omitted
A Copilot IDE session with no user message and no assistant text SHALL stay out of the list.

#### Scenario: Empty draft
- **WHEN** a Copilot IDE session file has no user message and no assistant text
- **THEN** the list omits that session

### Requirement: Copilot IDE background agent omitted
A Copilot background-agent database SHALL stay out of the list.

#### Scenario: Background agent database
- **WHEN** the Copilot IDE root contains a background-agent database and a chat session
- **THEN** the list includes the chat session and omits the background-agent database

### Requirement: Copilot IDE session listed beside another id
An id that exists as a Copilot IDE session and as a Cursor session or a Copilot CLI session SHALL appear as both rows. The Copilot IDE row's source cell SHALL be `Cp-IDE`.

#### Scenario: Same id in Copilot IDE and the chat store
- **WHEN** the same id is a Copilot IDE session and an agent chat
- **THEN** the list has both rows and the Copilot IDE row's source cell is `Cp-IDE`

### Requirement: Copilot IDE title
A Copilot IDE row's title SHALL be the session title when that title has text. An empty title SHALL use the first line of the first user message. When that line is empty, the title SHALL be the session id.

#### Scenario: Session title
- **WHEN** the session title is non-empty
- **THEN** the row title is that title

#### Scenario: First user line
- **WHEN** the session title is empty and the first user message's first line is non-empty
- **THEN** the row title is that line

#### Scenario: No title text
- **WHEN** the session title and the user messages are empty
- **THEN** the row title is the session id

### Requirement: Copilot IDE list time
A Copilot IDE row's time SHALL be the session's latest timestamp, shown in the catalog's local time form. When the latest timestamp is missing, the row SHALL use the creation timestamp.

#### Scenario: Latest time
- **WHEN** a Copilot IDE session has a latest timestamp
- **THEN** the row shows that time in the catalog's local time form

### Requirement: Copilot IDE workspace
The workspace column SHALL show the last segment of the session's workspace path. When that path is missing, the column SHALL be empty and This workspace SHALL omit the row.

#### Scenario: Workspace path
- **WHEN** the session has a workspace path and the CLI is launched from that path
- **THEN** the row shows the last segment of that path and This workspace includes the row

#### Scenario: Missing workspace path
- **WHEN** the session has no workspace path
- **THEN** the workspace column is empty and This workspace omits the row

### Requirement: Export a Copilot IDE session
Passing the id of a Copilot IDE session SHALL write that session through the same HTML or Markdown export as an agent chat. The written page SHALL omit the source cell.

#### Scenario: HTML export
- **WHEN** the user passes a Copilot IDE session id
- **THEN** the export contains the user message and the assistant text and omits the source cell

### Requirement: Copilot IDE turn text
The default Copilot IDE transcript SHALL show each user message and the assistant's visible text. Consecutive assistant text SHALL share one Agent heading until the next user message. An empty assistant reply SHALL add no Agent heading.

#### Scenario: User and assistant
- **WHEN** a turn has a user message and assistant text
- **THEN** the export shows that user message and that assistant text under one Agent heading

#### Scenario: Empty assistant
- **WHEN** a turn has a user message and no assistant text
- **THEN** the export shows the user message and no Agent heading for that turn

### Requirement: Copilot IDE session with no turns
A Copilot IDE session with no user message and no assistant text SHALL be reported with `Chat has no transcript: {id}`, and the CLI SHALL write no file.

#### Scenario: Empty session id
- **WHEN** the user passes the id of a Copilot IDE session that has no turns
- **THEN** the CLI reports that the chat has no transcript and writes no file

### Requirement: Copilot IDE tool caption
With `--tools`, a Copilot IDE tool call SHALL show one caption and SHALL omit the tool result and the command text.

#### Scenario: Read a file
- **WHEN** the user passes `--tools` and the tool reads a file
- **THEN** the caption is `Read` plus that path and the result is omitted

#### Scenario: Create a file
- **WHEN** the user passes `--tools` and the tool creates a file
- **THEN** the caption is `Create` plus that path and the result is omitted

#### Scenario: Find files
- **WHEN** the user passes `--tools` and the tool searches for files by a pattern
- **THEN** the caption is `Glob` plus that pattern and the result is omitted

#### Scenario: Run a command
- **WHEN** the user passes `--tools` and the tool runs a command with a description
- **THEN** the caption is `Ran` plus that description and the command text is omitted

#### Scenario: Edit a file
- **WHEN** the user passes `--tools` and the tool edits a file
- **THEN** the caption is `Edit` plus that path and the result is omitted

### Requirement: Copilot IDE verbose detail
`--verbose` SHALL include Copilot IDE tool captions and tool result text, and SHALL omit command text.

#### Scenario: Tool result
- **WHEN** the user passes `--verbose` and a turn has a tool result
- **THEN** the export includes that tool result and omits the command text

### Requirement: Copilot IDE icons omitted
The export SHALL omit Copilot avatar addresses and icon addresses.

#### Scenario: Avatar address
- **WHEN** a Copilot IDE session carries an avatar address
- **THEN** the export omits that address

### Requirement: Read-only Copilot IDE store
The tool SHALL leave Copilot IDE session files byte-for-byte unchanged.

#### Scenario: Bytes unchanged
- **WHEN** a Copilot IDE session is exported
- **THEN** the session file has the same bytes as before the export

### Requirement: Unreadable Copilot IDE session
An unreadable Copilot IDE session SHALL be omitted with the warning `Unreadable Copilot IDE session {id}: {error}`, and the command SHALL still list the other sessions.

#### Scenario: Session cannot be read
- **WHEN** a Copilot IDE session file cannot be read
- **THEN** the warning names that session and the other sessions remain in the list

### Requirement: VS Code agent-host session
A VS Code agent-host chat whose linked Copilot event log has a user or assistant message SHALL appear as one `Cp-IDE` row. A tombstoned agent-host chat SHALL stay out of the list. A missing agent-host database SHALL add no rows and SHALL NOT fail the command.

#### Scenario: Linked event log
- **WHEN** the VS Code root's agent-host database names a Copilot event log that has a user message and assistant text
- **THEN** the list contains one `Cp-IDE` row for that log, titled with the agent-host summary when that summary has text

#### Scenario: Tombstoned chat
- **WHEN** an agent-host chat is tombstoned
- **THEN** the list omits that chat

#### Scenario: Missing agent-host database
- **WHEN** the VS Code root has no agent-host database
- **THEN** the command does not fail because that database is missing

### Requirement: Rider event-log transcript
A Rider session whose conversation id names a Copilot event log with a user or assistant message SHALL appear once, as `Cp-IDE`. Export of that id SHALL show the log's user and assistant text. The Nitrite file SHALL stay byte-for-byte unchanged.

#### Scenario: Conversation id joins once
- **WHEN** a Rider database names a conversation id and that id's event log has a user message
- **THEN** the list contains one `Cp-IDE` row for that id and does not also list it as `Cp-CLI`

#### Scenario: Export uses the event log
- **WHEN** the user exports that id
- **THEN** the export contains the event log's user message and assistant text and the Nitrite file bytes are unchanged

### Requirement: Unlisted Copilot event log
A Copilot event log that has a user or assistant message, and that is not already a catalog row, SHALL appear as one `Cp-CLI` row.

#### Scenario: Log without a database row
- **WHEN** the Copilot root has an event log with a user message and the session database has no row for that id
- **THEN** the list contains one `Cp-CLI` row for that log

### Requirement: Product description names Cursor and Copilot
The README, the package description, the contributor instructions, and the command help SHALL name both Cursor and Copilot.

#### Scenario: README names both products
- **WHEN** the README is read
- **THEN** it names Cursor and Copilot, and it names `Copilot-IDE`, `Cp-IDE`, and `copilot-ide`

#### Scenario: README keeps the export sentences
- **WHEN** the README is read
- **THEN** it contains `Enter asks for a file name.` and `HTML is the default.`

#### Scenario: Package description
- **WHEN** the package description is read
- **THEN** it names Cursor and Copilot

#### Scenario: Contributor instructions
- **WHEN** the contributor instructions are read
- **THEN** they name Cursor and Copilot

#### Scenario: Command help
- **WHEN** the user passes `--help`
- **THEN** the help text contains `copilot-ide`
