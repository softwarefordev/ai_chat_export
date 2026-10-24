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

### Requirement: Picker leaves chats intact
The picker SHALL NOT delete or modify chats in the local store.

#### Scenario: Backspace in the picker
- **WHEN** the user presses Backspace while the picker is open
- **THEN** the selected chat remains in the store

### Requirement: Theme shown before export
The picker SHALL show the HTML theme that Enter will write.

#### Scenario: Default theme is visible
- **WHEN** the picker opens without a light-theme request
- **THEN** the picker shows the dark theme as the theme that will be written

#### Scenario: Light theme is visible
- **WHEN** the user requested the light theme and the picker is open
- **THEN** the picker shows the light theme as the theme that will be written

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
The CLI SHALL name each file it writes from the chat title and write it in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. A default export SHALL write the HTML file. Passing `--markdown` SHALL also write the Markdown file. Passing `--name` without an output directory SHALL write only that path. Without a chat id, `--name` SHALL write no file. When a file this export writes already exists, the export SHALL replace that file.

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
The HTML file SHALL use the dark theme unless the user requests light at export time. The requested theme SHALL be part of the written file.

#### Scenario: Dark by default
- **WHEN** the user exports without requesting light
- **THEN** the HTML file renders in the dark theme

#### Scenario: Light when requested
- **WHEN** the user requests the light theme
- **THEN** the HTML file renders in the light theme

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
- **THEN** the name line shows the end of the draft and the chat columns stay aligned

#### Scenario: Movement while naming
- **WHEN** the user presses up or down while the name line is open
- **THEN** the selected chat stays the same and the list remains on screen
