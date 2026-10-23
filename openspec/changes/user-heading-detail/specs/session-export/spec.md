# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: User heading
HTML and Markdown SHALL label each user section User. An agent section SHALL stay labeled Agent.

#### Scenario: User query heading
- **WHEN** a user query is exported to HTML and Markdown
- **THEN** the HTML heading is User and the Markdown heading is User

#### Scenario: Agent heading unchanged
- **WHEN** an agent stretch is exported
- **THEN** its heading is Agent
