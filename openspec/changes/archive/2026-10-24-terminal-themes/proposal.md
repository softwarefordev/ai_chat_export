# Proposal

## Why

The HTML page has one dark web palette and one light web palette. A reader who wants the transcript to look like a console has no green-screen choice, and the default is the web dark theme.

## What Changes

- **BREAKING:** `--theme` accepts `terminal-dark`, `terminal-light`, `dark-web`, and `light-web`. The names `dark` and `light` are no longer accepted.
- `terminal-dark` is the default. It is a dark green-screen page: phosphor text, a monospace face, and square panels.
- `terminal-light` is the same console on pale green paper.
- `dark-web` and `light-web` keep today's dark and light palettes, the serif transcript, the sans navigator, the rounded panels, and the gold User edge.
- On every theme, User and Agent sections keep different panels, and User keeps a left edge. On a terminal theme that edge is amber. System and Context stay on the shared panel.
- The picker footer shows the theme name that will be written, so a default open shows `terminal-dark`.
- Markdown still has no color theme.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `session-export`: The export theme set is `terminal-dark`, `terminal-light`, `dark-web`, and `light-web`, with `terminal-dark` as the default. Terminal pages use a console face and square panels, and User and Agent stay distinct on every theme.

## Impact

- `ai_chat_export/render_html.py` adds the two terminal palettes and the console face and corners.
- `ai_chat_export/__main__.py` changes the `--theme` choices and the default.
- `README.md` names the four themes and the new default.
- `tests/test_render.py`, `tests/test_picker.py`, and `tests/test_export.py` follow the new names and palettes.
