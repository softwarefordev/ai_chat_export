# ai-chat-export

Export a local Cursor or Copilot chat to an HTML page. The page follows the chat: the prompt you typed, then the assistant's visible text. The user section is labeled User. Consecutive assistant replies share one Agent heading until the next prompt. The HTML page lists user turns, and each entry jumps to that turn. HTML is the default. `--markdown` writes the Markdown file instead of the HTML page.

HTML uses terminal-dark unless you name terminal-light, dark-web, or light-web. A user turn shows the query only. `--detail` adds the conversation summary and Cursor command blocks after that query. `--tools` adds one caption per tool call. `--verbose` adds those captions plus system text, injected context, reasoning, and raw tool output. `--verbose` does not add the summary or command blocks.

The installed command is `ai-chat-export`. From a checkout, `python -m ai_chat_export` runs the same tool.

```bash
ai-chat-export --help
python -m ai_chat_export --help
```

Open the picker for Cursor agent chats under `~/.cursor/chats`, Cursor IDE transcripts under `~/.cursor/projects`, Copilot CLI sessions under `~/.copilot`, VS Code Copilot chats in the Visual Studio Code user directory, and Rider or Visual Studio Copilot chats in the local github-copilot directory:

```bash
ai-chat-export
```

The list shows the title, workspace, source, and time in aligned columns. The source column reads `Cu-CLI` for a Cursor agent chat, `Cu-IDE` for a Cursor IDE transcript, `Cp-CLI` for a Copilot CLI session, and `Cp-IDE` for a Copilot IDE session. Under the workspace header, `s` cycles All sources, Cursor-CLI, Cursor-IDE, Copilot-CLI, and Copilot-IDE. `--source cursor-cli`, `--source cursor-ide`, `--source copilot-cli`, or `--source copilot-ide` opens on that source, and `s` can move on from there. Repeat `--source` to name more than one. A session stored in both Cursor places appears once, from the agent chat. A Copilot CLI session and a Copilot IDE session each keep their own row. Up and down move. Left and right switch `All chats` and `This workspace`. Enter asks for a file name. The chat list stays on screen. The line starts as the title file name. Enter on that line writes the file. Esc on the name line returns to the list. Esc on the list closes. The footer shows the theme that will be written. `i` shows the selected chat id.

Export one chat without the picker:

```bash
ai-chat-export --id <chat-id> --out ./exports
ai-chat-export --id <chat-id> --theme terminal-light
ai-chat-export --id <chat-id> --tools
ai-chat-export --id <chat-id> --verbose
ai-chat-export --id <chat-id> --detail
ai-chat-export --id <chat-id> --markdown
ai-chat-export --id <chat-id> --name ./exports/session.html
```

`--chats-root` points at a different catalog directory. `--projects-root` points at a different IDE transcript directory. `--copilot-root` points at a different Copilot CLI session directory. `--vscode-root` points at a different VS Code user directory. `--copilot-ide-root` points at a different Rider and Visual Studio Copilot directory. Files are named from the chat title. A generated name whose stem is a Windows reserved device name, such as `CON` or `NUL`, uses the chat id instead. An existing HTML file is replaced. `--markdown` replaces an existing Markdown file and leaves an existing HTML file unchanged. `--name` is written as given. `--name` requires `--id`. Passing `--name` with `--out` is an error.

The tool only reads Cursor chat stores and Copilot session stores. It does not delete chats, modify transcripts, or call Cursor or Copilot.
