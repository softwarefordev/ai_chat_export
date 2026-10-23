"""Render a transcript as one self-contained HTML file."""

from __future__ import annotations

import html
import re

from session_export.transcript import Block, Transcript

_DARK = {
    "bg": "#161616",
    "text": "#f2f2f2",
    "muted": "#a3a3a3",
    "time": "#e0b040",
    "panel": "#222222",
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
    sections = "\n".join(_section(block) for block in transcript.blocks)
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
            ".tool { font-family: Consolas, ui-monospace, monospace; color: var(--mark); margin: 0.35rem 0; }",
            "pre { background: var(--code); padding: 0.8rem 1rem; overflow: auto; }",
            "code { font-family: Consolas, ui-monospace, monospace; }",
            "footer { color: var(--muted); font-size: 0.9rem; }",
            "img { max-width: 100%; }",
        ]
    )


def _section(block: Block) -> str:
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
    return (
        f'<section class="{html.escape(block.kind)}">\n'
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
