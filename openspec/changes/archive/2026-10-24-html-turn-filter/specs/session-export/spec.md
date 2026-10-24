# Spec Delta

## ADDED Requirements

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
