# Spec Delta

## MODIFIED Requirements

### Requirement: Default transcript
The default transcript SHALL include each typed user prompt's query portion and the assistant's visible text, in conversation order. The query portion SHALL be the inner text of each `user_query` element. It SHALL omit timestamp markup, Cursor command blocks, other injected context, tool captions, system text, assistant reasoning, and raw tool output. When a typed user prompt has no `user_query` element, the query portion SHALL be that typed text.

#### Scenario: Typed prompt beside injected context
- **WHEN** a user turn contains a query element and injected context
- **THEN** the default transcript includes the query text and omits the injected context

#### Scenario: Query inside markup
- **WHEN** a user turn's typed text wraps the query in a `user_query` element and also contains a timestamp element
- **THEN** the default transcript includes the inner query text and omits the tags and the timestamp element

#### Scenario: Tool call omitted
- **WHEN** the user exports without `--tools` and without `--verbose`, and a turn contains a tool call and a tool result
- **THEN** the transcript omits the caption and the raw result

### Requirement: Verbose transcript
Verbose mode SHALL add system text, injected context, assistant reasoning, raw tool output, and tool captions, in conversation order. Additions that belong to an agent stretch SHALL stay inside that stretch's Agent heading. Verbose mode SHALL NOT, by itself, add a Cursor command block to the You turn.

#### Scenario: Verbose includes a tool result
- **WHEN** the user exports with verbose mode and a turn has a tool result
- **THEN** the transcript includes that raw tool output inside the Agent heading

#### Scenario: Verbose keeps one Agent heading
- **WHEN** verbose mode exports two assistant messages and a tool result before the next typed prompt
- **THEN** one Agent heading contains both messages, the caption, and the tool result

#### Scenario: Verbose without detail
- **WHEN** the user exports with verbose mode and without `--detail`, and a user turn has a Cursor command block and other injected context
- **THEN** the transcript includes the other injected context and does not add the command block to the You turn

## ADDED Requirements

### Requirement: User turn detail
The CLI SHALL omit Cursor command blocks unless the user passes `--detail`. A shown block SHALL be the inner text of each `cursor_commands` element and SHALL appear once inside that You section, after the query.

#### Scenario: Detail shows the command
- **WHEN** the user passes `--detail` and a user turn contains a `cursor_commands` element
- **THEN** the You section includes that element's inner text after the query

#### Scenario: Detail without a command
- **WHEN** the user passes `--detail` and a user turn has no `cursor_commands` element
- **THEN** the You section contains the query and no command block

#### Scenario: Both flags show the command once
- **WHEN** the user passes `--detail` and `--verbose` and a user turn contains a command block inside injected context
- **THEN** the command block appears once, in the You section, and the injected context does not repeat it

### Requirement: Turn timestamp
Each visible You section and each Agent section SHALL show a formatted timestamp in the catalog style: abbreviated month, day, year, and 12-hour time. A You section SHALL use the timestamp recorded on that user turn. An Agent section SHALL use the timestamp of the user turn that opened that stretch. A section with no recorded turn timestamp SHALL omit the time. The chat header timestamp SHALL remain.

#### Scenario: User turn time
- **WHEN** a visible user turn records `Friday, Oct 23, 2026, 11:13 AM (UTC-7)`
- **THEN** the You section shows `Oct 23, 2026 11:13 AM`

#### Scenario: Agent stretch time
- **WHEN** an Agent section follows a user turn with that timestamp
- **THEN** the Agent section shows the same formatted time

#### Scenario: Missing turn time
- **WHEN** a visible section has no recorded turn timestamp
- **THEN** that section omits the time and the chat header still shows the chat's updated time

#### Scenario: Both outputs
- **WHEN** the user exports HTML and Markdown for a turn that has a timestamp
- **THEN** both files show that turn's formatted time
