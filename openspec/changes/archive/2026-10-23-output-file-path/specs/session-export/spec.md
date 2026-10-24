# Spec Delta

## MODIFIED Requirements

### Requirement: Output location and names
The CLI SHALL name each file it writes from the chat title and write it in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. A default export SHALL write the HTML file. Passing `--markdown` SHALL also write the Markdown file. Passing `--name` without an output directory SHALL write only that path. When a file this export writes already exists, the export SHALL replace that file.

#### Scenario: Default directory
- **WHEN** the user does not supply an output directory and does not pass `--name`
- **THEN** the HTML file is created in the current directory

#### Scenario: Supplied directory
- **WHEN** the user supplies an output directory and does not pass `--markdown` and does not pass `--name`
- **THEN** the HTML file is created in that directory

#### Scenario: Existing HTML file
- **WHEN** the HTML target already exists and the user does not pass `--markdown` and does not pass `--name`
- **THEN** the CLI replaces the HTML file, prints its path, and exits successfully

#### Scenario: Existing Markdown file
- **WHEN** a Markdown file is already present and the user does not pass `--markdown` and does not pass `--name`
- **THEN** that Markdown file is unchanged

#### Scenario: Markdown beside HTML
- **WHEN** the user passes `--markdown` and does not pass `--name` and either target file already exists
- **THEN** the CLI replaces the existing target files, writes any missing target, prints both paths, and exits successfully

#### Scenario: Neighboring file
- **WHEN** the output directory contains a file that is not a target of this export
- **THEN** that file is unchanged

#### Scenario: Named path
- **WHEN** the user passes `--name` with a file path and does not pass `--markdown` or an output directory
- **THEN** the CLI writes the HTML export to that path, prints that path, and does not create a title-named file

#### Scenario: Named Markdown path
- **WHEN** the user passes `--name` and `--markdown` and does not pass an output directory
- **THEN** the CLI writes the Markdown export to that path, prints that path, and does not write a second file

#### Scenario: Name and output directory
- **WHEN** the user passes `--name` and an output directory
- **THEN** the CLI reports the conflict, writes no file, and exits unsuccessfully

#### Scenario: Relative named path
- **WHEN** the user passes `--name` with a relative file path and does not pass an output directory
- **THEN** that file is created relative to the current directory

#### Scenario: Existing named file
- **WHEN** the path passed to `--name` already exists and the user does not pass an output directory
- **THEN** the CLI replaces that file, prints its path, and exits successfully

#### Scenario: Missing parent directory
- **WHEN** the parent directory of the `--name` path does not exist and the user does not pass an output directory
- **THEN** the CLI creates that directory and writes the file there

#### Scenario: Name is a directory
- **WHEN** the path passed to `--name` is an existing directory
- **THEN** the CLI reports the error, writes no file, and exits unsuccessfully
