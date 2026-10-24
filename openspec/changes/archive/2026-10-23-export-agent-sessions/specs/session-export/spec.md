# Spec Delta

## Purpose

List local Cursor agent chats and export one chat to an HTML page and a Markdown transcript that follow the conversation.

## ADDED Requirements

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
Running the CLI without a chat id SHALL open a picker. Up and down SHALL move the selection, left and right SHALL switch scope, Enter SHALL export the selected chat, and Esc SHALL close the picker without writing files.

#### Scenario: Export from the picker
- **WHEN** the user presses Enter on a selected chat that has a conversation
- **THEN** the CLI writes that chat's HTML and Markdown exports

#### Scenario: Close without export
- **WHEN** the user presses Esc
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
A successful export SHALL write one HTML file and one Markdown file from the same filtered transcript, and SHALL print both paths.

#### Scenario: Both files are written
- **WHEN** a chat with a conversation is exported
- **THEN** the HTML file and the Markdown file exist and the CLI prints both paths

### Requirement: Output location and names
The CLI SHALL name both files from the chat title and write them in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name.

#### Scenario: Default directory
- **WHEN** the user does not supply an output directory
- **THEN** both files are created in the current directory

#### Scenario: Supplied directory
- **WHEN** the user supplies an output directory
- **THEN** both files are created in that directory

#### Scenario: Existing file
- **WHEN** either target file already exists
- **THEN** the CLI reports the conflict and leaves both target paths unchanged

### Requirement: Default transcript
The default transcript SHALL include each typed user prompt and the assistant's visible text, in conversation order. It SHALL omit tool captions, system text, injected context, assistant reasoning, and raw tool output.

#### Scenario: Typed prompt beside injected context
- **WHEN** a user turn contains typed text and injected context
- **THEN** the default transcript includes the typed text and omits the injected context

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
Verbose mode SHALL add system text, injected context, assistant reasoning, raw tool output, and tool captions, in conversation order. Additions that belong to an agent stretch SHALL stay inside that stretch's Agent heading.

#### Scenario: Verbose includes a tool result
- **WHEN** the user exports with verbose mode and a turn has a tool result
- **THEN** the transcript includes that raw tool output inside the Agent heading

#### Scenario: Verbose keeps one Agent heading
- **WHEN** verbose mode exports two assistant messages and a tool result before the next typed prompt
- **THEN** one Agent heading contains both messages, the caption, and the tool result

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
- **WHEN** a chat is exported
- **THEN** the Markdown file contains the same visible turns as the HTML file

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
