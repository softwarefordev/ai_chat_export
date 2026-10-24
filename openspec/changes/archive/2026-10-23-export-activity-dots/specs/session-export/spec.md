# Spec Delta

## ADDED Requirements

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
