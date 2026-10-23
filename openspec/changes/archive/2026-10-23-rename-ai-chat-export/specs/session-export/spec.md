# Spec Delta

## MODIFIED Requirements

### Requirement: Project name
The tool SHALL present itself as `ai-chat-export` in help text and in the README. The installed command SHALL be `ai-chat-export`.

#### Scenario: Help names the tool
- **WHEN** the user asks for help
- **THEN** the usage line names `ai-chat-export`

#### Scenario: README names the tool
- **WHEN** the README is read
- **THEN** its title is `ai-chat-export`

#### Scenario: Installed command
- **WHEN** the package declares its console command
- **THEN** that command is `ai-chat-export`

### Requirement: Module invocation
The tool SHALL run as the Python module `ai_chat_export`.

#### Scenario: Module entry
- **WHEN** the user runs `python -m ai_chat_export`
- **THEN** the tool runs
