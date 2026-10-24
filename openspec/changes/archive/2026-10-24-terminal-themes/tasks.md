# Tasks

## 1. Four HTML themes

- [x] 1.1 Add `terminal-dark`, `terminal-light`, `dark-web`, and `light-web` palettes, with the terminal face and square corners and the web face and rounded corners, and make `terminal-dark` the renderer default. Verify a render test that the default page uses `#071207`, a monospace face, and square corners, that User and Agent panels differ and the User edge is amber, that `dark-web` still uses `#161616`, Georgia, rounded corners, and the gold edge, that `light-web` uses `#f7f7f4`, that `terminal-light` uses `#e6f5df`, and that the page contains no script and no `http`.
- [x] 1.2 Accept only those four `--theme` names, default `terminal-dark` on the command and on `export_session`, and reject `dark` and `light` before reading the store. Verify help lists the four names and the default, and that `--theme dark` exits unsuccessfully and writes no file.

## 2. Picker, README, and Markdown

- [x] 2.1 Show the chosen theme name in the picker footer, with `terminal-dark` when no theme was requested. Verify a picker test that the default frame contains `theme: terminal-dark` and that a requested `terminal-light`, `dark-web`, or `light-web` frame shows that name.
- [x] 2.2 Update the README so the default is `terminal-dark` and the sample theme command is `--theme terminal-light`. Verify the README contains `terminal-dark` and `--theme terminal-light`, and that `HTML is the default.` still holds.
- [x] 2.3 Leave the Markdown export uncolored, and verify a markdown render contains no `#071207` and no `#e6f5df`.

## Workflow follow-up

- Archive the change after the project's review requirements are satisfied.
