# Spec Delta

## ADDED Requirements

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
