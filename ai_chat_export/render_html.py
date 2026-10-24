"""Render a transcript as one self-contained HTML file."""

from __future__ import annotations

import base64
import html
import re
from datetime import datetime

from ai_chat_export.transcript import SECTION_HEADINGS, Block, Transcript

_WEB_BODY = '18px/1.5 Georgia, "Iowan Old Style", Palatino, serif'
_WEB_NAV = '"Segoe UI", system-ui, sans-serif'
_TERM_BODY = "18px/1.5 Consolas, ui-monospace, monospace"
_TERM_NAV = "Consolas, ui-monospace, monospace"


def _theme(colors: dict[str, str], *, body: str, nav: str, radius: str) -> dict[str, str]:
    theme = dict(colors)
    theme["body"] = body
    theme["nav"] = nav
    theme["radius"] = radius
    return theme


_DARK_WEB = _theme(
    {
        "bg": "#161616",
        "text": "#f2f2f2",
        "muted": "#a3a3a3",
        "time": "#e0b040",
        "panel": "#222222",
        "user": "#2c261c",
        "agent": "#1e2428",
        "mark": "#e0b040",
        "rule": "#3a3a3a",
        "code": "#101010",
    },
    body=_WEB_BODY,
    nav=_WEB_NAV,
    radius="8px",
)

_LIGHT_WEB = _theme(
    {
        "bg": "#f7f7f4",
        "text": "#1c1c1c",
        "muted": "#5e5e5e",
        "time": "#8a5a00",
        "panel": "#ffffff",
        "user": "#f6efe4",
        "agent": "#f3f5f7",
        "mark": "#8a5a00",
        "rule": "#d9d4cc",
        "code": "#f0ece4",
    },
    body=_WEB_BODY,
    nav=_WEB_NAV,
    radius="8px",
)

_TERMINAL_DARK = _theme(
    {
        "bg": "#071207",
        "text": "#c6f7c0",
        "muted": "#6ea86a",
        "time": "#e2c15a",
        "panel": "#0c1a10",
        "user": "#12301a",
        "agent": "#0b1610",
        "mark": "#e2c15a",
        "rule": "#1e3a24",
        "code": "#040a05",
    },
    body=_TERM_BODY,
    nav=_TERM_NAV,
    radius="0",
)

_TERMINAL_LIGHT = _theme(
    {
        "bg": "#e6f5df",
        "text": "#0e3a16",
        "muted": "#3f6b45",
        "time": "#7a5b12",
        "panel": "#f4fbf1",
        "user": "#d7f0c8",
        "agent": "#e7f3e2",
        "mark": "#7a5b12",
        "rule": "#b7d4b0",
        "code": "#f7fff4",
    },
    body=_TERM_BODY,
    nav=_TERM_NAV,
    radius="0",
)

_THEMES = {
    "terminal-dark": _TERMINAL_DARK,
    "terminal-light": _TERMINAL_LIGHT,
    "dark-web": _DARK_WEB,
    "light-web": _LIGHT_WEB,
}

THEME_NAMES = tuple(_THEMES)

_RASTER_TYPES = frozenset({"image/png", "image/jpeg", "image/gif", "image/webp"})
_ASCII_WHITESPACE = frozenset(" \t\n\r\v\f")


def render_html(
    transcript: Transcript,
    *,
    title: str,
    workspace: str,
    timestamp: str,
    theme: str = "terminal-dark",
) -> str:
    palette = _THEMES.get(theme, _THEMES["terminal-dark"])
    turns = sum(block.kind == "you" for block in transcript.blocks)
    css = _stylesheet(palette, turns)
    sections = _sections(transcript.blocks)
    navigator = _navigator(transcript.blocks)
    footer = _footer(transcript.footer)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>\n{css}\n</style>\n"
        "</head>\n"
        "<body>\n"
        f"{navigator}"
        "<article>\n"
        "<header>\n"
        f"<h1>{html.escape(title)}</h1>\n"
        '<p class="meta">'
        f'<span class="workspace">{html.escape(workspace)}</span>'
        f'<span class="time">{html.escape(timestamp)}</span>'
        "</p>\n"
        "</header>\n"
        f"{sections}\n"
        f"{footer}\n"
        "</article>\n"
        "</body>\n"
        "</html>\n"
    )


def render_assistant(text: str) -> str:
    """Render the small assistant subset: fences, indented code, lists, paragraphs, inline code."""
    return _blocks(text)


def _stylesheet(palette: dict[str, str], turns: int) -> str:
    rules = [
            ":root {",
            f"  --bg: {palette['bg']};",
            f"  --text: {palette['text']};",
            f"  --muted: {palette['muted']};",
            f"  --time: {palette['time']};",
            f"  --panel: {palette['panel']};",
            f"  --user: {palette['user']};",
            f"  --agent: {palette['agent']};",
            f"  --mark: {palette['mark']};",
            f"  --rule: {palette['rule']};",
            f"  --code: {palette['code']};",
            "}",
            "body {",
            "  margin: 0;",
            "  background: var(--bg);",
            "  color: var(--text);",
            f"  font: {palette['body']};",
            "}",
            "article { max-width: 44rem; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }",
            "header { border-bottom: 1px solid var(--rule); margin-bottom: 1.5rem; }",
            "h1 { font-size: 1.8rem; font-weight: 600; margin: 0 0 0.4rem; }",
            "h2 { font-size: 0.85rem; letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); margin: 0 0 0.6rem; }",
            ".meta { display: flex; justify-content: space-between; gap: 1rem; color: var(--muted); }",
            ".time { color: var(--time); }",
            f"section {{ background: var(--panel); border: 1px solid var(--rule); border-radius: {palette['radius']}; padding: 1rem 1.1rem; margin: 0 0 1rem; }}",
            "section.you { background: var(--user); border-left: 3px solid var(--mark); scroll-margin-top: 5rem; }",
            "section.you:target { outline: 2px solid var(--mark); }",
            "section.agent { background: var(--agent); }",
            "section.system, section.context { background: var(--panel); }",
            "nav { position: sticky; top: 0; overflow: auto; max-height: 40vh; background: var(--bg); border-bottom: 1px solid var(--rule); padding: 0.8rem 1.2rem; font-family: "
            + palette["nav"]
            + "; }",
            "nav ol { list-style: none; margin: 0; padding: 0; }",
            "nav a { display: flex; flex-direction: column; gap: 0; min-width: 0; color: var(--text); text-decoration: none; }",
            "nav li { display: flex; align-items: flex-start; gap: 0.5rem; }",
            "nav li + li { margin-top: 0.85rem; }",
            "nav .label { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
            "nav .time { font-size: 10px; line-height: 1; white-space: nowrap; }",
            "nav button { display: none; font: inherit; color: var(--text); background: var(--bg); border: 1px solid var(--rule); }",
            "body:has(nav input:checked) nav button { display: block; }",
            "nav form > button:first-child { position: sticky; top: 0; z-index: 1; }",
            "body:has(nav input:checked) article section { display: none; }",
            "@media (min-width: 70rem) {",
            "  body { display: grid; grid-template-columns: 30rem minmax(0, 1fr); align-items: start; }",
            "  nav { max-height: 100vh; border-bottom: 0; border-right: 1px solid var(--rule); }",
            "}",
            ".tool { font-family: Consolas, ui-monospace, monospace; color: var(--mark); margin: 0.35rem 0; }",
            "pre { background: var(--code); padding: 0.8rem 1rem; overflow: auto; }",
            "code { font-family: Consolas, ui-monospace, monospace; }",
            "footer { color: var(--muted); font-size: 0.9rem; }",
            "img { max-width: 100%; }",
    ]
    for number in range(1, turns + 1):
        rules.append(
            "body:has(#keep-"
            f'{number}:checked) article [data-turn="{number}"] {{ display: block; }}'
        )
    return "\n".join(rules)


def _sections(blocks: list[Block]) -> str:
    rendered: list[str] = []
    number = 0
    turn = 0
    for block in blocks:
        anchor = ""
        mark = 0
        if block.kind == "you":
            number += 1
            turn = number
            anchor = f"user-{number}"
            mark = turn
        elif block.kind == "agent" and turn:
            mark = turn
        rendered.append(_section(block, anchor, mark))
    return "\n".join(rendered)


def _navigator(blocks: list[Block]) -> str:
    items: list[str] = []
    number = 0
    for block in blocks:
        if block.kind != "you":
            continue
        number += 1
        stamp = ""
        if block.timestamp:
            stamp = f'<span class="time">{html.escape(_compact_nav_time(block.timestamp))}</span>'
        label = html.escape(_nav_label(block))
        items.append(
            "<li>"
            f'<input type="checkbox" id="keep-{number}">'
            f'<a href="#user-{number}">{stamp}<span class="label">{label}</span></a>'
            "</li>"
        )
    body = "\n".join(items)
    clear = '<button type="reset">Clear filter</button>'
    return (
        "<nav>\n"
        "<form>\n"
        f"{clear}\n"
        "<ol>\n"
        f"{body}\n"
        "</ol>\n"
        f"{clear}\n"
        "</form>\n"
        "</nav>\n"
    )


def _compact_nav_time(stamp: str) -> str:
    match = re.fullmatch(
        r"(?P<month>[A-Za-z]{3}) (?P<day>\d{1,2}), (?P<year>\d{4}) "
        r"(?P<hour>\d{2}):(?P<minute>\d{2}) (?P<ampm>AM|PM)",
        stamp,
    )
    if match is None:
        return stamp
    try:
        month = datetime.strptime(match.group("month"), "%b").month
    except ValueError:
        return stamp
    hour = int(match.group("hour"))
    if match.group("ampm") == "PM" and hour != 12:
        hour += 12
    if match.group("ampm") == "AM" and hour == 12:
        hour = 0
    year = int(match.group("year")) % 100
    day = int(match.group("day"))
    minute = int(match.group("minute"))
    return f"{year:02d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"


def _nav_label(block: Block) -> str:
    text = block.text.strip()
    if text:
        return text.split("\n", 1)[0].strip()
    if block.images:
        return "Image"
    return "User"


def _section(block: Block, anchor: str = "", turn: int = 0) -> str:
    heading = SECTION_HEADINGS.get(block.kind, block.kind)
    if block.pieces:
        body = "\n".join(_piece_html(piece) for piece in block.pieces)
    else:
        prose = render_assistant(block.text) if block.kind == "agent" else _plain_paragraphs(block.text)
        detail = _plain_paragraphs(block.detail)
        captions = "\n".join(
            f'<p class="tool">&gt; {html.escape(caption)}</p>' for caption in block.captions
        )
        images = "\n".join(
            tag for media, data in block.images if (tag := _image_html(media, data))
        )
        body = "\n".join(part for part in (prose, detail, captions, images) if part)
    ident = f' id="{html.escape(anchor)}"' if anchor else ""
    mark = f' data-turn="{turn}"' if turn else ""
    return (
        f'<section class="{html.escape(block.kind)}"{ident}{mark}>\n'
        f"<h2>{_heading(block, heading)}</h2>\n"
        f"{body}\n"
        "</section>"
    )


def _heading(block: Block, label: str) -> str:
    if block.timestamp and block.kind in ("you", "agent"):
        return f'{html.escape(label)} <span class="time">{html.escape(block.timestamp)}</span>'
    return html.escape(label)


def _piece_html(piece) -> str:
    if piece.kind == "text":
        return render_assistant(piece.text)
    if piece.kind == "caption":
        return f'<p class="tool">&gt; {html.escape(piece.text)}</p>'
    if piece.kind == "image":
        return _image_html(piece.media, piece.text)
    label = SECTION_HEADINGS.get(piece.kind, piece.kind)
    return f"<h3>{label}</h3>\n{_plain_paragraphs(piece.text)}"


def _image_html(media: str, data: str) -> str:
    kind = "image/jpeg" if media == "image/jpg" else media
    if kind not in _RASTER_TYPES:
        return ""
    compact = "".join(character for character in data if character not in _ASCII_WHITESPACE)
    try:
        raw = base64.b64decode(compact, validate=True)
    except ValueError:
        return ""
    encoded = base64.b64encode(raw).decode("ascii")
    return f'<img alt="attachment" src="data:{kind};base64,{encoded}">'


def _footer(lines: list[str]) -> str:
    if not lines:
        return ""
    items = "\n".join(f"<p>{html.escape(line)}</p>" for line in lines)
    return f"<footer>\n{items}\n</footer>"


def _plain_paragraphs(text: str) -> str:
    if not text:
        return ""
    chunks = re.split(r"\n\s*\n", text)
    return "\n".join(f"<p>{html.escape(chunk).replace(chr(10), '<br>')}</p>" for chunk in chunks if chunk)


def _blocks(text: str) -> str:
    if not text:
        return ""
    lines = text.split("\n")
    pieces: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            index += 1
            buffer: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                buffer.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            pieces.append("<pre><code>" + html.escape("\n".join(buffer)) + "</code></pre>")
            continue
        if line.startswith("    ") and line.strip():
            buffer = []
            while index < len(lines) and lines[index].startswith("    "):
                buffer.append(lines[index][4:])
                index += 1
            pieces.append("<pre><code>" + html.escape("\n".join(buffer)) + "</code></pre>")
            continue
        if re.match(r"^(\*|-|\d+\.) ", line):
            items: list[str] = []
            while index < len(lines) and re.match(r"^(\*|-|\d+\.) ", lines[index]):
                item = re.sub(r"^(\*|-|\d+\.) ", "", lines[index])
                items.append("<li>" + _inline(item) + "</li>")
                index += 1
            pieces.append("<ul>" + "".join(items) + "</ul>")
            continue
        if not line.strip():
            index += 1
            continue
        buffer = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not _block_start(lines[index]):
            buffer.append(lines[index])
            index += 1
        pieces.append("<p>" + _inline(" ".join(buffer)) + "</p>")
    return "\n".join(pieces)


def _block_start(line: str) -> bool:
    return line.startswith("```") or line.startswith("    ") or bool(re.match(r"^(\*|-|\d+\.) ", line))


def _inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    rendered: list[str] = []
    for part in parts:
        if len(part) >= 2 and part.startswith("`") and part.endswith("`"):
            rendered.append("<code>" + html.escape(part[1:-1]) + "</code>")
        else:
            rendered.append(html.escape(part))
    return "".join(rendered)
