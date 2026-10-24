"""Render a transcript as Markdown."""

from __future__ import annotations

from ai_chat_export.transcript import SECTION_HEADINGS, Block, Transcript


def _piece_markdown(block: Block) -> list[str]:
    parts: list[str] = []
    for piece in block.pieces:
        if piece.kind == "text" and piece.text:
            parts.append(piece.text)
            parts.append("")
        elif piece.kind == "caption":
            parts.append(f"- {piece.text}")
            parts.append("")
        elif piece.kind == "image":
            parts.append(f"![attachment](data:{piece.media};base64,{piece.text})")
            parts.append("")
        elif piece.kind == "reasoning":
            parts.extend([f"### {SECTION_HEADINGS['reasoning']}", "", piece.text, ""])
        elif piece.kind == "tool_output":
            parts.extend([f"### {SECTION_HEADINGS['tool_output']}", "", piece.text, ""])
    return parts


def render_markdown(
    transcript: Transcript,
    *,
    title: str,
    workspace: str,
    timestamp: str,
) -> str:
    parts = [f"# {title}", "", f"{workspace} · {timestamp}", ""]
    for block in transcript.blocks:
        heading = SECTION_HEADINGS.get(block.kind, block.kind)
        if block.timestamp and block.kind in ("you", "agent"):
            heading = f"{heading} · {block.timestamp}"
        parts.append(f"## {heading}")
        parts.append("")
        if block.pieces:
            parts.extend(_piece_markdown(block))
            continue
        if block.text:
            parts.append(block.text)
            parts.append("")
        if block.detail:
            parts.append(block.detail)
            parts.append("")
        for caption in block.captions:
            parts.append(f"- {caption}")
        if block.captions:
            parts.append("")
        for media, data in block.images:
            parts.append(f"![attachment](data:{media};base64,{data})")
            parts.append("")
    if transcript.footer:
        parts.append("## Notes")
        parts.append("")
        for line in transcript.footer:
            parts.append(f"- {line}")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"
