# Spec Delta

## MODIFIED Requirements

### Requirement: Paired HTML and Markdown
A successful export SHALL write one HTML file from the filtered transcript and SHALL print that path. Passing `--markdown` SHALL also write one Markdown file from that same transcript and SHALL print both paths.

#### Scenario: HTML by default
- **WHEN** a chat with a conversation is exported without `--markdown` into a directory that has no Markdown file
- **THEN** the HTML file exists, the CLI prints its path, and no Markdown file exists

#### Scenario: Markdown when requested
- **WHEN** the user passes `--markdown`
- **THEN** the HTML file and the Markdown file exist and the CLI prints both paths

### Requirement: Output location and names
The CLI SHALL name each file it writes from the chat title and write it in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. A default export SHALL write the HTML file. Passing `--markdown` SHALL also write the Markdown file. When a file this export writes already exists, the export SHALL replace that file.

#### Scenario: Default directory
- **WHEN** the user does not supply an output directory
- **THEN** the HTML file is created in the current directory

#### Scenario: Supplied directory
- **WHEN** the user supplies an output directory
- **THEN** the HTML file is created in that directory

#### Scenario: Existing HTML file
- **WHEN** the HTML target already exists and the user does not pass `--markdown`
- **THEN** the CLI replaces the HTML file, prints its path, and exits successfully

#### Scenario: Existing Markdown file
- **WHEN** a Markdown file is already present and the user does not pass `--markdown`
- **THEN** that Markdown file is unchanged

#### Scenario: Markdown beside HTML
- **WHEN** the user passes `--markdown` and either target file already exists
- **THEN** the CLI replaces the existing target files, writes any missing target, prints both paths, and exits successfully

#### Scenario: Neighboring file
- **WHEN** the output directory contains a file that is not a target of this export
- **THEN** that file is unchanged

### Requirement: Markdown has no theme
The Markdown file SHALL contain the same prompts, assistant text, and shown tool captions as the HTML file for that export. It SHALL NOT encode a color theme.

#### Scenario: Matching turns
- **WHEN** the user passes `--markdown`
- **THEN** the Markdown file contains the same visible turns as the HTML file and does not encode a color theme
