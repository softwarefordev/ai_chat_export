"""Render a transcript as one self-contained HTML file."""

from __future__ import annotations

import html
import re
from datetime import datetime

from session_export.transcript import Block, Transcript

_DARK = {
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
}

_LIGHT = {
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
}

_HEADINGS = {
    "you": "User",
    "agent": "Agent",
    "system": "System",
    "context": "Context",
    "reasoning": "Reasoning",
    "tool_output": "Tool output",
}


def render_html(
    transcript: Transcript,
    *,
    title: str,
    workspace: str,
    timestamp: str,
    theme: str = "dark",
) -> str:
    palette = _LIGHT if theme == "light" else _DARK
    css = _stylesheet(palette)
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


def _stylesheet(palette: dict[str, str]) -> str:
    return "\n".join(
        [
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
            '  font: 18px/1.5 Georgia, "Iowan Old Style", Palatino, serif;',
            "}",
            "article { max-width: 44rem; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }",
            "header { border-bottom: 1px solid var(--rule); margin-bottom: 1.5rem; }",
            "h1 { font-size: 1.8rem; font-weight: 600; margin: 0 0 0.4rem; }",
            "h2 { font-size: 0.85rem; letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); margin: 0 0 0.6rem; }",
            ".meta { display: flex; justify-content: space-between; gap: 1rem; color: var(--muted); }",
            ".time { color: var(--time); }",
            "section { background: var(--panel); border: 1px solid var(--rule); border-radius: 8px; padding: 1rem 1.1rem; margin: 0 0 1rem; }",
            "section.you { background: var(--user); border-left: 3px solid var(--mark); scroll-margin-top: 5rem; }",
            "section.you:target { outline: 2px solid var(--mark); }",
            "section.agent { background: var(--agent); }",
            "section.system, section.context { background: var(--panel); }",
            'nav { position: sticky; top: 0; overflow: auto; max-height: 40vh; background: var(--bg); border-bottom: 1px solid var(--rule); padding: 0.8rem 1.2rem; font-family: "Segoe UI", system-ui, sans-serif; }',
            "nav ol { list-style: none; margin: 0; padding: 0; }",
            "nav a { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; color: var(--text); text-decoration: none; }",
            "nav .label { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
            "nav .time { font-size: 10px; white-space: nowrap; }",
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
    )


def _sections(blocks: list[Block]) -> str:
    rendered: list[str] = []
    number = 0
    for block in blocks:
        anchor = ""
        if block.kind == "you":
            number += 1
            anchor = f"user-{number}"
        rendered.append(_section(block, anchor))
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
            f'<li><a href="#user-{number}">{stamp}<span class="label">{label}</span></a></li>'
        )
    body = "\n".join(items)
    return f"<nav>\n<ol>\n{body}\n</ol>\n</nav>\n"


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


def _section(block: Block, anchor: str = "") -> str:
    heading = _HEADINGS.get(block.kind, block.kind)
    if block.pieces:
        body = "\n".join(_piece_html(piece) for piece in block.pieces)
    else:
        prose = render_assistant(block.text) if block.kind == "agent" else _plain_paragraphs(block.text)
        detail = _plain_paragraphs(block.detail)
        captions = "\n".join(
            f'<p class="tool">&gt; {html.escape(caption)}</p>' for caption in block.captions
        )
        images = "\n".join(_image_html(media, data) for media, data in block.images)
        body = "\n".join(part for part in (prose, detail, captions, images) if part)
    ident = f' id="{html.escape(anchor)}"' if anchor else ""
    return (
        f'<section class="{html.escape(block.kind)}"{ident}>\n'
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
    label = "Reasoning" if piece.kind == "reasoning" else "Tool output"
    return f"<h3>{label}</h3>\n{_plain_paragraphs(piece.text)}"


def _image_html(media: str, data: str) -> str:
    return f'<img alt="attachment" src="data:{html.escape(media)};base64,{data}">'


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
