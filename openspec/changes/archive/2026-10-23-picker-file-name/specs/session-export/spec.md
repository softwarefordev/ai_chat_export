# Spec Delta

## MODIFIED Requirements

### Requirement: Interactive picker
Running the CLI without a chat id SHALL open a picker. Up and down SHALL move the selection, left and right SHALL switch scope, Enter SHALL open a file-name line for the selected chat and SHALL NOT write a file yet, and Esc SHALL close the picker without writing files. The name line SHALL start as the title file name, or the chat id when the chat has no title. Confirming that line SHALL write the export under that file name in the output directory.

#### Scenario: Export from the picker
- **WHEN** the user presses Enter on a selected chat that has a conversation
- **THEN** the name line shows the title file name and no file is written yet

#### Scenario: Confirm the default name
- **WHEN** the user presses Enter on the unchanged name line
- **THEN** the title-named file is written in the output directory

#### Scenario: Edited name
- **WHEN** the user types a different file name and presses Enter
- **THEN** that file is written in the output directory and the title-named file is not written

#### Scenario: Empty name
- **WHEN** the user clears the name line and presses Enter
- **THEN** the title-named file is written in the output directory

#### Scenario: Markdown default name
- **WHEN** the user passes `--markdown` and presses Enter on a selected chat
- **THEN** the name line ends in `.md`

#### Scenario: Esc from the name line
- **WHEN** the user presses Esc on the name line
- **THEN** the chat list returns and no file is written

#### Scenario: Close without export
- **WHEN** the user presses Esc on the chat list
- **THEN** the CLI exits without writing files

### Requirement: Output location and names
The CLI SHALL name each file it writes from the chat title and write it in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. A default export SHALL write the HTML file. Passing `--markdown` SHALL also write the Markdown file. Without a chat id, `--name` SHALL write no file. When a file this export writes already exists, the export SHALL replace that file.

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

#### Scenario: Name without a chat id
- **WHEN** the user passes `--name` and does not pass a chat id
- **THEN** the CLI reports the error, does not open the picker, and writes no file

#### Scenario: Named path by chat id
- **WHEN** the user passes a chat id and `--name` with a file path and does not pass `--markdown` or an output directory
- **THEN** the CLI writes the HTML export to that path, prints that path, and does not open the picker

#### Scenario: Name and output directory
- **WHEN** the user passes a chat id, `--name`, and an output directory
- **THEN** the CLI reports the conflict, writes no file, and does not open the picker
