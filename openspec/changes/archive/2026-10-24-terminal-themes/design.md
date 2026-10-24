# Design

## Context

See proposal.md for why. `render_html` chooses `_LIGHT` when the theme is `light` and `_DARK` otherwise. Both palettes share one stylesheet: Georgia for the transcript, a sans navigator, and `border-radius: 8px` on sections. User and Agent differ by panel color and a left edge colored with `--mark`. `--theme` accepts `dark` and `light`, and the default is `dark`. The picker prints that string as `theme: <name>`. Tests reject `http` and a script element on the whole page. A render test expects the sans navigator face on the default page.

## Goals / Non-Goals

**Goals:**

- Bake one of four palettes into the file, with `terminal-dark` as the default.
- Give the terminal pages a console face and square sections while the web pages keep their current face, corners, and colors.

**Non-Goals:**

- A theme switch inside the page.
- Coloring the Markdown export.
- Keeping `dark` and `light` as accepted flag values.

## Decisions

### One palette map, including face and corners

Each theme is a palette plus a body face, a navigator face, and a section radius. The stylesheet stays shared. Web themes keep the current hex values, Georgia for the body, the sans navigator, radius `8px`, and the gold `--mark`. Terminal themes set radius `0` and use `Consolas, ui-monospace, monospace` for the body and the navigator.

`terminal-dark`: background `#071207`, text `#c6f7c0`, muted `#6ea86a`, time and mark `#e2c15a`, panel `#0c1a10`, user `#12301a`, agent `#0b1610`, rule `#1e3a24`, code `#040a05`.

`terminal-light`: background `#e6f5df`, text `#0e3a16`, muted `#3f6b45`, time and mark `#7a5b12`, panel `#f4fbf1`, user `#d7f0c8`, agent `#e7f3e2`, rule `#b7d4b0`, code `#f7fff4`.

The amber mark is the User edge on both terminal themes. Agent has a different panel and no edge. System and Context stay on `--panel`.

Alternative: recolor only, and leave Georgia and rounded cards. That keeps a web page in green paint. The console face and square corners are what make the terminal themes read as a screen.

### The flag names are the only names

`--theme` choices are `terminal-dark`, `terminal-light`, `dark-web`, and `light-web`. The default on the parser, on `export_session`, and on `render_html` is `terminal-dark`. An unknown theme value inside the renderer also uses `terminal-dark`. Argparse rejects `dark` and `light` before the store is read. The picker prints the chosen name, so the footer is `theme: terminal-dark` unless another allowed name was passed.

The README sentence `HTML is dark unless you ask for light.` becomes a sentence that names `terminal-dark` as the default and the other three names. The sample `--theme light` command becomes `--theme terminal-light`.

## Risks / Trade-offs

- [Existing exports and scripts pass `--theme dark` or `--theme light`] → Those names are rejected. The README and help show the four names.
- [The default-page test looks for the sans navigator] → That assertion moves to a web-theme page. The terminal page asserts the monospace face.
- [Pure phosphor green is hard to read at 10px] → The text greens above are dimmer than `#00ff00`, and the time color is amber.

## Migration Plan

No store migration. A new export without `--theme` writes `terminal-dark`. Pass `dark-web` or `light-web` to get the previous palettes.
