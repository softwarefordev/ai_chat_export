# Spec Delta

## ADDED Requirements

### Requirement: Safe embedded image
The HTML page SHALL embed an image only when its media type is `image/png`, `image/jpeg`, `image/gif`, or `image/webp` and its payload is base64. Media type `image/jpg` SHALL be embedded as `image/jpeg`. Any other image SHALL be omitted from the image tag. The page SHALL contain no script.

#### Scenario: PNG stays embedded
- **WHEN** a turn includes an image of type `image/png` whose payload is base64
- **THEN** the page shows that image and contains no script element

#### Scenario: JPEG alias
- **WHEN** a turn includes an image of type `image/jpg` whose payload is base64
- **THEN** the page embeds that image as `image/jpeg`

#### Scenario: Markup in the payload
- **WHEN** an image payload contains a quote followed by a script element
- **THEN** the page contains no script element and does not treat that payload as markup

#### Scenario: SVG is omitted
- **WHEN** an image media type is `image/svg+xml`
- **THEN** the page does not embed that payload

#### Scenario: HTML media type is omitted
- **WHEN** an image media type is `text/html`
- **THEN** the page does not embed that payload and contains no script element

### Requirement: Store path stays read-only
The CLI SHALL open the chat database at its given path in read-only mode. A `?` or `#` in that path SHALL remain part of the path and SHALL NOT select another open mode. The database file SHALL be unchanged.

#### Scenario: Question mark in the path
- **WHEN** the database path contains `?`
- **THEN** the CLI reads that path read-only and does not create or change a database at the path truncated at `?`

#### Scenario: Hash in the path
- **WHEN** the database path contains `#`
- **THEN** the CLI reads that path read-only and does not create or change a database at the path truncated at `#`

## MODIFIED Requirements

### Requirement: Output location and names
The CLI SHALL name each file it writes from the chat title and write it in the current directory. A supplied output directory SHALL be used instead of the current directory. A chat with no title SHALL use its id as the file name. A default export SHALL write the HTML file. Passing `--markdown` SHALL also write the Markdown file. Passing `--name` without an output directory SHALL write only that path. Without a chat id, `--name` SHALL write no file. When a file this export writes already exists, the export SHALL replace that file. A generated stem that is `CON`, `PRN`, `AUX`, `NUL`, `COM1` through `COM9`, or `LPT1` through `LPT9`, compared without regard to case, SHALL use the chat id instead. When that id is also one of those names, the stem SHALL be the id plus `-export`. A path passed to `--name` SHALL be written as given.

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

#### Scenario: Named path
- **WHEN** the user passes a chat id and `--name` with a file path and does not pass `--markdown` or an output directory
- **THEN** the CLI writes the HTML export to that path, prints that path, does not create a title-named file, and does not open the picker

#### Scenario: Named path by chat id
- **WHEN** the user passes a chat id and `--name` with a file path and does not pass `--markdown` or an output directory
- **THEN** the CLI writes the HTML export to that path, prints that path, and does not open the picker

#### Scenario: Named Markdown path
- **WHEN** the user passes a chat id, `--name`, and `--markdown` and does not pass an output directory
- **THEN** the CLI writes the Markdown export to that path, prints that path, and does not write a second file

#### Scenario: Name and output directory
- **WHEN** the user passes a chat id, `--name`, and an output directory
- **THEN** the CLI reports the conflict, writes no file, does not open the picker, and exits unsuccessfully

#### Scenario: Relative named path
- **WHEN** the user passes a chat id and `--name` with a relative file path and does not pass an output directory
- **THEN** that file is created relative to the current directory

#### Scenario: Existing named file
- **WHEN** the user passes a chat id and the path passed to `--name` already exists and the user does not pass an output directory
- **THEN** the CLI replaces that file, prints its path, and exits successfully

#### Scenario: Missing parent directory
- **WHEN** the user passes a chat id and the parent directory of the `--name` path does not exist and the user does not pass an output directory
- **THEN** the CLI creates that directory and writes the file there

#### Scenario: Name is a directory
- **WHEN** the user passes a chat id and the path passed to `--name` is an existing directory
- **THEN** the CLI reports the error, writes no file, and exits unsuccessfully

#### Scenario: Reserved title
- **WHEN** the chat title is `CON` and the user exports without `--name`
- **THEN** the written file uses the chat id as its stem and is not named `CON.html`

#### Scenario: Reserved markdown title
- **WHEN** the chat title is `nul` and the user passes `--markdown` and does not pass `--name`
- **THEN** the written file uses the chat id as its stem and is not named `nul.md`

#### Scenario: Reserved id
- **WHEN** the chat has no title, its id is `CON`, and the user exports without `--name`
- **THEN** the written stem is `CON-export`

#### Scenario: Explicit reserved path
- **WHEN** the user passes a chat id and `--name` whose file name is `CON.html`
- **THEN** the CLI writes that path

### Requirement: Interactive picker
Running the CLI without a chat id SHALL open a picker. Up and down SHALL move the selection, left and right SHALL switch scope, Enter SHALL open a file-name line for the selected chat and SHALL NOT write a file yet, and Esc SHALL close the picker without writing files. The name line SHALL start as the title file name, or the chat id when the chat has no title. Confirming that line SHALL write the export under that file name in the output directory. A stem that is `CON`, `PRN`, `AUX`, `NUL`, `COM1` through `COM9`, or `LPT1` through `LPT9`, compared without regard to case, SHALL be replaced with the chat id, or with the id plus `-export` when the id is also one of those names. The replacement applies to the name line's starting value and to the name confirmed from the line.

#### Scenario: Export from the picker
- **WHEN** the user presses Enter on a selected chat that has a conversation
- **THEN** the same screen still shows the selected chat and the theme, the name line shows the title file name and says that typing edits it, and no file is written yet

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
- **THEN** the chat list returns without the name line and no file is written

#### Scenario: Close without export
- **WHEN** the user presses Esc on the chat list
- **THEN** the CLI exits without writing files

#### Scenario: Reserved default name
- **WHEN** the selected chat's title is `CON` and the user opens the name line
- **THEN** the name line shows the chat id with the export extension and does not show `CON.html`

#### Scenario: Reserved confirmed draft
- **WHEN** the user sets the name line to `COM1` and presses Enter
- **THEN** the written file uses the chat id as its stem and is not named `COM1.html`
