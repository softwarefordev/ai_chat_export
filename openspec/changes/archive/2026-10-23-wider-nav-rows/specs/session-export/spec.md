# Spec Delta

## ADDED Requirements

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
