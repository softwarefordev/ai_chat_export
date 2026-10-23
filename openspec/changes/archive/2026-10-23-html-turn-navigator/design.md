# Design

## Context

See proposal.md for why. `render_html` paints every section with one `--panel` color. Sections already carry the classes `you`, `agent`, `system`, and `context`. The dark and light palettes are baked into one `<style>` block. Tests reject a `<script` tag and the letters `http` anywhere in the page. Markdown is a separate renderer.

## Goals / Non-Goals

**Goals:**

- Give User and Agent different panel colors, with a gold edge on User only.
- Add a sticky navigator of fragment links to User sections.
- Keep the page one file, with no script and no external address.

**Non-Goals:**

- A script that highlights the turn currently on screen.
- Scroll snapping, a theme toggle, or a Markdown navigator.
- Changing which turns the transcript includes.

## Decisions

### Two panel variables

Each palette gains `--user` and `--agent`. `section.you` uses `--user` and a left border in the existing gold `--mark`. `section.agent` uses `--agent` and no gold edge. System and Context stay on `--panel`, which remains different from both.

Dark: user `#2c261c`, agent `#1e2428`, panel `#222222`. Light: user `#f6efe4`, agent `#f3f5f7`, panel `#ffffff`.

Alternative: one shared panel and only a gold edge on User. The edge helps, and the warm versus cool fill is what separates the cards while scrolling.

### Sticky fragment list

The navigator is a `<nav>` before the article. At `min-width: 52rem` the page is two columns: a `16rem` list beside the transcript. Below that, the list is a band above the transcript with `max-height: 40vh`. In both layouts the nav is `position: sticky; top: 0; overflow: auto`.

Each User section gets `id="user-N"`, counting User sections from 1 in document order. The matching link is `href="#user-N"`. Agent, System, and Context sections are not linked. A transcript with no User section renders an empty nav.

The link text is the turn time, when present, plus the query up to the first line break. The query span is `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`, so the ellipsis is drawn by the browser rather than inserted into the file. A User section with no query text and an image uses the label `Image`. A User section with neither uses `User`.

`section.you:target` draws a gold outline. `scroll-margin-top: 5rem` keeps the heading below the narrow sticky band.

Alternative: an inline script and `IntersectionObserver` to mark the turn on screen. The page forbids scripts, and fragment links plus `:target` cover the jump.

### README

One sentence says the HTML page lists user turns and each entry jumps to that turn.

## Risks / Trade-offs

- [The whole-page test rejects the letters `http`] → Navigator links are fragments only. Do not add an external address.
- [Unit tests cannot click a link or paint an ellipsis] → Assert the `href` and `id` pairs, `position: sticky`, `text-overflow: ellipsis`, and the `:target` rule.
- [A one-line query is copied into the nav] → The entry stops at the first line break, and CSS clips the rest of that line.
- [A long chat makes a long list] → The nav scrolls inside itself.

## Migration Plan

A later export replaces the HTML file. No store migration.
