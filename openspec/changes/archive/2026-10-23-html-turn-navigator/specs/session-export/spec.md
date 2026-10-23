# Spec Delta

## ADDED Requirements

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
