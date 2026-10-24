# Spec Delta

## ADDED Requirements

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
