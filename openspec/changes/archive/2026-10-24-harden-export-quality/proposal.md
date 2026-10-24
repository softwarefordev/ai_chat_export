# Proposal

## Why

A review of `ai_chat_export` found three places where the tool can break guarantees it already makes. An image payload can split the HTML page open, a store path can change how SQLite is opened, and a chat title can become a Windows device name. File-name rules, section headings, and the theme list are also copied in more than one module, so those guarantees are easy to let drift.

## What Changes

- An embedded HTML image is written only when its media type is an allowlisted raster type and its payload is base64. Any other image is left out of the `img` tag. A valid PNG, JPEG, GIF, or WebP still embeds. The page still has no script and no external address.
- `store.db` is opened through a quoted read-only SQLite URI. `?` and `#` in the path cannot change the open mode. The store files stay unchanged.
- A generated file name whose stem is a Windows reserved device name (`CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`) is not used. The CLI falls back to the chat id, as it does for an empty title. The picker uses the same rule for the default name and for a confirmed draft.
- File-name sanitizing, section headings, and the theme list each live in one place. The four theme names, the heading words, and ordinary titles stay as they are.
- The activity helper uses a CapWords name, a successful export does not rely on `assert`, and public functions that lack types gain them. Ruff checks the package and the tests.
- No new command-line flags. Picker keys, transcript filters, and which file `--markdown` writes stay as they are.

This change does not add a plugin system, rewrite the conversation reader, HTML-escape Markdown body text, or correct older spec text that still names `ai-session-exporter` or a paired HTML-and-Markdown write. Those are separate from this review.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `session-export`: HTML image embedding stays inside the document; the chat store stays read-only when its path contains URI characters; a reserved device name is not used as an export file name.

## Impact

- `ai_chat_export/render_html.py`: image tags.
- `ai_chat_export/transcript.py`: image media and payload passed through to the renderer.
- `ai_chat_export/store.py`: SQLite open URI.
- `ai_chat_export/__main__.py` and `ai_chat_export/picker.py`: one file-name sanitizer.
- `pyproject.toml`: Ruff configuration. No runtime dependencies.
- Tests for image markup, the read-only open, and reserved file names.
