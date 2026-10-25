"""Build the filtered transcript from conversation messages."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime

from ai_chat_export.catalog import format_datetime


@dataclass
class Piece:
    kind: str
    text: str
    media: str = ""


@dataclass
class Block:
    kind: str
    text: str = ""
    captions: list[str] = field(default_factory=list)
    images: list[tuple[str, str]] = field(default_factory=list)
    pieces: list[Piece] = field(default_factory=list)
    timestamp: str = ""
    detail: str = ""


@dataclass
class Transcript:
    blocks: list[Block] = field(default_factory=list)
    footer: list[str] = field(default_factory=list)


SECTION_HEADINGS = {
    "you": "User",
    "agent": "Agent",
    "system": "System",
    "context": "Context",
    "reasoning": "Reasoning",
    "tool_output": "Tool output",
}


def build_transcript(
    messages: list[dict],
    prompts: list[str],
    *,
    verbose: bool = False,
    show_tools: bool = False,
    show_detail: bool = False,
    skipped: list[str] | None = None,
    unlinked_images: list[str] | None = None,
) -> Transcript:
    include_captions = bool(verbose or show_tools)
    transcript = Transcript()
    stretch: list[Piece] | None = None
    stretch_time = ""

    def flush() -> None:
        nonlocal stretch
        if not stretch:
            stretch = None
            return
        text = "\n\n".join(piece.text for piece in stretch if piece.kind == "text" and piece.text)
        captions = [piece.text for piece in stretch if piece.kind == "caption"]
        images = [(piece.media, piece.text) for piece in stretch if piece.kind == "image"]
        transcript.blocks.append(
            Block(
                "agent",
                text=text,
                captions=captions,
                images=images,
                pieces=list(stretch),
                timestamp=stretch_time,
            )
        )
        stretch = None

    def ensure() -> None:
        nonlocal stretch
        if stretch is None:
            stretch = []

    for message in messages:
        role = message.get("role")
        content = message.get("content")
        if role == "system":
            if verbose:
                flush()
                transcript.blocks.append(Block("system", text=_plain_text(content)))
            continue
        if role == "user":
            parts = _text_parts(content)
            typed, context = split_user_text(parts, prompts)
            images = _image_parts(content)
            query = query_text(typed)
            detail = detail_text(parts) if show_detail else ""
            turn_time = turn_timestamp(parts)
            if query or images or detail:
                flush()
                stretch_time = turn_time
                transcript.blocks.append(
                    Block(
                        "you",
                        text=query,
                        images=images,
                        timestamp=turn_time,
                        detail=detail,
                    )
                )
            if verbose:
                context_body = context_text(
                    _preamble_parts(typed) + context,
                    hide_commands=show_detail,
                )
                if context_body:
                    transcript.blocks.append(Block("context", text=context_body))
            continue
        if role == "assistant":
            text = _joined(content, "text")
            captions = [caption(part) for part in _parts(content, "tool-call")] if include_captions else []
            reasoning = _joined(content, "reasoning") if verbose else ""
            images = _image_parts(content)
            if not (text or captions or reasoning or images):
                continue
            ensure()
            if text:
                stretch.append(Piece("text", text))
            for label in captions:
                stretch.append(Piece("caption", label))
            if reasoning:
                stretch.append(Piece("reasoning", reasoning))
            for media, data in images:
                stretch.append(Piece("image", data, media))
            continue
        if role == "tool" and verbose:
            result = _tool_result(content)
            if not result:
                continue
            ensure()
            stretch.append(Piece("tool_output", result))
    flush()
    for blob_id in skipped or []:
        transcript.footer.append(f"Skipped unrecognized data {blob_id}")
    for blob_id in unlinked_images or []:
        transcript.footer.append(f"Image not attached to a turn: {blob_id}")
    return transcript


def split_user_text(parts: list[str], prompts: list[str]) -> tuple[list[str], list[str]]:
    usable = [prompt for prompt in prompts if prompt.strip()]
    if not usable:
        if not parts:
            return [], []
        return [parts[-1]], parts[:-1]
    typed: list[str] = []
    context: list[str] = []
    for part in parts:
        if any(prompt in part for prompt in usable):
            typed.append(part)
        else:
            context.append(part)
    if typed:
        return typed, context
    if not parts:
        return [], []
    return [parts[-1]], parts[:-1]


_TURN_TIME = re.compile(
    r"^(?P<weekday>[A-Za-z]+), "
    r"(?P<month>[A-Za-z]{3}) "
    r"(?P<day>\d{1,2}), "
    r"(?P<year>\d{4}), "
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2}) "
    r"(?P<ampm>AM|PM) "
    r"\(UTC[+-]\d+\)$"
)


_ELEMENT = re.compile(r"</?[A-Za-z_][\w.-]*>")


def query_text(typed: list[str]) -> str:
    extracted: list[str] = []
    saw_query = False
    for part in typed:
        found = element_texts(part, "user_query")
        if found:
            saw_query = True
            extracted.extend(found)
    if saw_query:
        return "\n\n".join(extracted)
    plain = [part.strip() for part in typed if part.strip() and not _ELEMENT.search(part)]
    return "\n\n".join(plain)


def _preamble_parts(typed: list[str]) -> list[str]:
    """Typed parts that are injected context, not a query or a detail-only block."""
    extras: list[str] = []
    for part in typed:
        if element_texts(part, "user_query") or not part.strip() or not _ELEMENT.search(part):
            continue
        remainder = part
        for name in ("conversation_summary", "cursor_commands", "timestamp"):
            remainder = strip_element(remainder, name)
        if remainder.strip():
            extras.append(part)
    return extras


def detail_text(parts: list[str]) -> str:
    chunks: list[str] = []
    for name in ("conversation_summary", "cursor_commands"):
        for part in parts:
            chunks.extend(element_texts(part, name))
    return "\n\n".join(chunks)


def turn_timestamp(parts: list[str]) -> str:
    for part in parts:
        found = element_texts(part, "timestamp")
        if found:
            return format_turn_time(found[0])
    return ""


def context_text(parts: list[str], *, hide_commands: bool) -> str:
    chunks: list[str] = []
    for part in parts:
        text = part
        if hide_commands:
            for name in ("cursor_commands", "conversation_summary"):
                text = strip_element(text, name)
        if text.strip():
            chunks.append(text.strip())
    return "\n\n".join(chunks)


def element_texts(text: str, name: str) -> list[str]:
    pattern = re.compile(rf"<{re.escape(name)}>(.*?)</{re.escape(name)}>", re.DOTALL)
    return [match.strip() for match in pattern.findall(text) if match.strip()]


def strip_element(text: str, name: str) -> str:
    pattern = re.compile(rf"<{re.escape(name)}>.*?</{re.escape(name)}>", re.DOTALL)
    return pattern.sub("", text).strip()


def format_turn_time(raw: str) -> str:
    text = " ".join(raw.split())
    match = _TURN_TIME.match(text)
    if not match:
        return text
    try:
        month = datetime.strptime(match.group("month"), "%b").month
    except ValueError:
        return text
    hour = int(match.group("hour"))
    if match.group("ampm") == "PM" and hour != 12:
        hour += 12
    if match.group("ampm") == "AM" and hour == 12:
        hour = 0
    moment = datetime(
        int(match.group("year")),
        month,
        int(match.group("day")),
        hour,
        int(match.group("minute")),
    )
    return format_datetime(moment)


def caption(part: dict) -> str:
    name = str(part.get("toolName") or "tool")
    args = _args(part.get("args"))
    if name == "Read":
        path = str(args.get("path") or "")
        return f"Read {path}".rstrip()
    if name == "Glob":
        pattern = str(args.get("glob_pattern") or "")
        return f"Glob {pattern}".rstrip()
    if name == "Shell":
        description = args.get("description")
        if isinstance(description, str) and description.strip():
            return f"Ran {description.strip()}"
        return "Ran command"
    if name == "Grep":
        pattern = str(args.get("pattern") or "")
        return f"Grep {pattern}".rstrip()
    if name == "Create":
        path = str(args.get("path") or "")
        return f"Create {path}".rstrip()
    if name == "Edit":
        path = str(args.get("path") or "")
        return f"Edit {path}".rstrip()
    return name


def _args(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, dict):
            return parsed
    return {}


def _parts(content, part_type: str) -> list[dict]:
    if not isinstance(content, list):
        return []
    return [
        part
        for part in content
        if isinstance(part, dict) and part.get("type") == part_type
    ]


def _text_parts(content) -> list[str]:
    if isinstance(content, str):
        return [content]
    return [str(part.get("text") or "") for part in _parts(content, "text")]


def _joined(content, part_type: str) -> str:
    if part_type == "text" and isinstance(content, str):
        return content
    return "\n\n".join(
        text for text in (str(part.get("text") or "") for part in _parts(content, part_type)) if text
    )


def _plain_text(content) -> str:
    if isinstance(content, str):
        return content
    return _joined(content, "text")


def _image_parts(content) -> list[tuple[str, str]]:
    images: list[tuple[str, str]] = []
    for part in _parts(content, "image"):
        data = part.get("data")
        if not isinstance(data, str) or not data:
            continue
        media = part.get("mediaType")
        if not isinstance(media, str) or not media:
            media = "image/png"
        images.append((media, data))
    return images


def _tool_result(content) -> str:
    chunks: list[str] = []
    for part in _parts(content, "tool-result"):
        result = part.get("result")
        if isinstance(result, str):
            chunks.append(result)
        else:
            chunks.append(json.dumps(result, indent=2))
    return "\n\n".join(chunks)
