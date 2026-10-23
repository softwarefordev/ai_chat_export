# Proposal

## Why

User and Agent sections share one panel, so a long reply hides the next prompt while scrolling. The page has no way to jump back to a user turn.

## What Changes

- User and Agent sections use different panels, so a prompt stands out from the reply that follows it.
- A sticky list of user prompts links to those sections. Each link is a fragment inside the same file.
- The page stays one file. The stylesheet stays inlined. The page still has no script and no external address.
- System and Context sections stay off the list. Markdown is unchanged.

## Capabilities

### New Capabilities

### Modified Capabilities

- `session-export`: The HTML page distinguishes User and Agent sections and adds a navigator that jumps to user turns.

## Impact

- `session_export/render_html.py`: section colors and the user-turn list.
- `tests/test_render.py`: distinct panels, fragment links, and the existing ban on scripts and external addresses.
- `README.md`: one sentence on the turn list.
