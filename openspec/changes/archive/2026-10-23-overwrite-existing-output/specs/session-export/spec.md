# Spec Delta

## MODIFIED Requirements

### Requirement: Output location and names
The CLI SHALL name both files from the chat title and write them in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. When a target file already exists, the export SHALL replace that file.

#### Scenario: Default directory
- **WHEN** the user does not supply an output directory
- **THEN** both files are created in the current directory

#### Scenario: Supplied directory
- **WHEN** the user supplies an output directory
- **THEN** both files are created in that directory

#### Scenario: Existing file
- **WHEN** either target file already exists
- **THEN** the CLI replaces the existing target files with the new export, prints both paths, and exits successfully

#### Scenario: Only one target exists
- **WHEN** the HTML target exists and the Markdown target does not
- **THEN** the HTML file is replaced, the Markdown file is created, and both contain the new export

#### Scenario: Neighboring file
- **WHEN** the output directory contains a file that is not either target
- **THEN** that file is unchanged
