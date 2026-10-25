"""Read Cursor IDE transcripts from a projects tree."""

from __future__ import annotations

import json
from pathlib import Path

from ai_chat_export.catalog import Chat, load_catalog, workspace_folder
from ai_chat_export.copilot import load_copilot_catalog, load_unlisted_session_logs
from ai_chat_export.copilot_ide import (
    load_copilot_ide_catalog,
    load_vscode_agent_sessions,
    load_vscode_catalog,
)
from ai_chat_export.store import Conversation
from ai_chat_export.transcript import element_texts, query_text


def load_sessions(
    chats_root: Path,
    projects_root: Path | None = None,
    warnings: list[str] | None = None,
    copilot_root: Path | None = None,
    vscode_root: Path | None = None,
    copilot_ide_root: Path | None = None,
    include_empty: bool = False,
) -> list[Chat]:
    notes = warnings if warnings is not None else []
    chats = load_catalog(chats_root, notes)
    if (
        projects_root is None
        and copilot_root is None
        and vscode_root is None
        and copilot_ide_root is None
    ):
        return chats
    if projects_root is not None:
        known = {chat.id for chat in chats}
        chats = chats + [row for row in load_ide_catalog(projects_root, notes) if row.id not in known]
    if copilot_root is not None:
        chats = chats + load_copilot_catalog(copilot_root, notes)
    if vscode_root is not None:
        chats = chats + load_vscode_catalog(vscode_root, notes, include_empty)
    if copilot_ide_root is not None:
        chats = chats + load_copilot_ide_catalog(
            copilot_ide_root, notes, include_empty, events_root=copilot_root
        )
    if vscode_root is not None and copilot_root is not None:
        chats = chats + load_vscode_agent_sessions(
            vscode_root, copilot_root, notes, include_empty
        )
    if copilot_root is not None:
        known = {chat.id for chat in chats}
        chats = chats + load_unlisted_session_logs(copilot_root, known, notes)
    chats.sort(key=lambda chat: (chat.updated_at_ms, chat.id), reverse=True)
    return chats


def load_ide_conversation(directory: Path) -> tuple[Conversation, list[str]]:
    path = Path(directory) / f"{Path(directory).name}.jsonl"
    conversation = Conversation()
    prompts: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            conversation.skipped.append(f"line {number}")
            continue
        if not isinstance(obj, dict):
            conversation.skipped.append(f"line {number}")
            continue
        if obj.get("type") == "turn_ended":
            continue
        role = obj.get("role")
        message = obj.get("message")
        if role not in {"user", "assistant"} or not isinstance(message, dict):
            conversation.skipped.append(f"line {number}")
            continue
        content = message.get("content")
        if role == "user":
            for part in _text_parts(content):
                prompts.extend(element_texts(part, "user_query"))
        conversation.messages.append({"role": role, "content": _adapt_content(content)})
    return conversation, prompts


def load_ide_catalog(root: Path, warnings: list[str] | None = None) -> list[Chat]:
    notes = warnings if warnings is not None else []
    root = Path(root)
    if not root.is_dir():
        return []
    rows: list[Chat] = []
    for jsonl in root.glob("*/agent-transcripts/*/*.jsonl"):
        if jsonl.parent.name != jsonl.stem:
            continue
        transcript_id = jsonl.stem
        try:
            title = _first_query_line(jsonl)
            updated_ms = int(jsonl.stat().st_mtime * 1000)
        except (OSError, UnicodeError) as exc:
            notes.append(f"Unreadable IDE transcript {transcript_id}: {exc}")
            continue
        cwd, workspace_name = _workspace(jsonl.parents[2])
        rows.append(
            Chat(
                id=transcript_id,
                title=title,
                cwd=cwd,
                workspace_name=workspace_name,
                updated_at_ms=updated_ms,
                has_store=True,
                path=jsonl.parent,
                source="ide",
            )
        )
    return rows


def _workspace(project: Path) -> tuple[str, str]:
    trusted = project / ".workspace-trusted"
    if trusted.is_file():
        try:
            payload = json.loads(trusted.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            payload = None
        if isinstance(payload, dict):
            path = payload.get("workspacePath")
            if isinstance(path, str) and path:
                return path, workspace_folder(path)
    return "", project.name


def _first_query_line(path: Path) -> str | None:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict) or obj.get("role") != "user":
                continue
            message = obj.get("message")
            if not isinstance(message, dict):
                continue
            query = query_text(_text_parts(message.get("content")))
            if not query.strip():
                continue
            first = query.splitlines()[0].strip()
            return first or None
    return None


def _adapt_content(content) -> list[dict]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if not isinstance(content, list):
        return []
    parts: list[dict] = []
    for part in content:
        if isinstance(part, str):
            parts.append({"type": "text", "text": part})
        elif isinstance(part, dict) and part.get("type") == "tool_use":
            raw_args = part.get("input")
            parts.append(
                {
                    "type": "tool-call",
                    "toolName": str(part.get("name") or "tool"),
                    "args": raw_args if isinstance(raw_args, dict) else {},
                }
            )
        elif isinstance(part, dict) and part.get("type") == "text":
            parts.append({"type": "text", "text": str(part.get("text") or "")})
        elif isinstance(part, dict):
            parts.append(part)
    return parts


def _text_parts(content) -> list[str]:
    if isinstance(content, str):
        return [content]
    if not isinstance(content, list):
        return []
    parts: list[str] = []
    for part in content:
        if isinstance(part, str):
            parts.append(part)
        elif isinstance(part, dict) and part.get("type") == "text":
            parts.append(str(part.get("text") or ""))
    return parts
