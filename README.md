# session-export

Export a local Cursor agent chat to an HTML page. The page follows the chat: the prompt you typed, then the assistant's visible text. The user section is labeled User. Consecutive assistant replies share one Agent heading until the next prompt. HTML is the default. `--markdown` also writes a Markdown file beside that page.

HTML is dark unless you ask for light. A user turn shows the query only. `--detail` adds the conversation summary and Cursor command blocks after that query. `--tools` adds one caption per tool call. `--verbose` adds those captions plus system text, injected context, reasoning, and raw tool output. `--verbose` does not add the summary or command blocks.

```bash
python -m session_export --help
```

Open the picker for chats under `~/.cursor/chats`:

```bash
python -m session_export
```

Up and down move. Left and right switch `All chats` and `This workspace`. Enter writes the files. Esc closes. The footer shows the theme that will be written.

Export one chat without the picker:

```bash
python -m session_export --id <chat-id> --out ./exports
python -m session_export --id <chat-id> --theme light
python -m session_export --id <chat-id> --tools
python -m session_export --id <chat-id> --verbose
python -m session_export --id <chat-id> --detail
python -m session_export --id <chat-id> --markdown
```

`--chats-root` points at a different catalog directory. Files are named from the chat title. An existing HTML file is replaced. `--markdown` also replaces an existing Markdown file.

The tool only reads the chat store. It does not delete chats or call Cursor.
