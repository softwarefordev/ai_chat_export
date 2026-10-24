"""Read GitHub Copilot CLI sessions."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ai_chat_export.catalog import Chat, workspace_folder
from ai_chat_export.store import Conversation, sqlite_uri


def load_copilot_conversation(directory: Path) -> tuple[Conversation, list[str], str | None]:
    directory = Path(directory)
    log = directory / "events.jsonl"
    if not log.exists():
        return _from_turns(directory), _turn_prompts(directory), None
    try:
        messages, prompts = _from_events(log)
    except (OSError, UnicodeError) as exc:
        return _from_turns(directory), _turn_prompts(directory), (
            f"Unreadable Copilot events {directory.name}: {exc}"
        )
    return _conversation(messages), prompts, None


def load_copilot_catalog(root: Path, warnings: list[str] | None = None) -> list[Chat]:
    notes = warnings if warnings is not None else []
    root = Path(root)
    if not root.is_dir():
        return []
    database = root / "session-store.db"
    if not database.is_file():
        return []
    try:
        connection = sqlite3.connect(sqlite_uri(database), uri=True)
        try:
            sessions = connection.execute(
                "SELECT id, cwd, summary, updated_at FROM sessions"
            ).fetchall()
            turns = connection.execute(
                "SELECT session_id, turn_index, user_message FROM turns ORDER BY turn_index"
            ).fetchall()
        finally:
            connection.close()
    except (sqlite3.Error, OSError) as exc:
        notes.append(f"Unreadable Copilot store: {exc}")
        return []
    first_lines = _first_lines(turns)
    rows: list[Chat] = []
    for session_id, cwd, summary, updated_at in sessions:
        if not isinstance(session_id, str) or not session_id:
            continue
        working = cwd if isinstance(cwd, str) else ""
        updated_ms, time_label = _updated(updated_at)
        rows.append(
            Chat(
                id=session_id,
                title=_title(summary, first_lines.get(session_id, "")),
                cwd=working,
                workspace_name=workspace_folder(working) if working else "",
                updated_at_ms=updated_ms,
                has_store=True,
                path=root / "session-state" / session_id,
                source="cp-cli",
                time_label=time_label,
            )
        )
    return rows


def _first_lines(turns: list[tuple]) -> dict[str, str]:
    lines: dict[str, str] = {}
    ordered = sorted(turns, key=lambda row: (row[0], row[1] if isinstance(row[1], int) else 0))
    for session_id, _index, message in ordered:
        if session_id in lines or not isinstance(session_id, str):
            continue
        if not isinstance(message, str):
            continue
        text = message.strip()
        if not text:
            continue
        lines[session_id] = text.splitlines()[0].strip()
    return lines


def _title(summary: object, first_line: str) -> str | None:
    if isinstance(summary, str) and summary.strip():
        return summary.strip()
    if first_line.strip():
        return first_line.strip()
    return None


def _updated(value: object) -> tuple[int, str | None]:
    if not isinstance(value, str):
        collapsed = ""
    else:
        collapsed = " ".join(value.split())
    if not collapsed:
        return 0, ""
    stamp = collapsed[:-1] + "+00:00" if collapsed.endswith("Z") else collapsed
    try:
        moment = datetime.fromisoformat(stamp)
    except ValueError:
        return 0, collapsed
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return int(moment.timestamp() * 1000), None


def _conversation(messages: list[dict]) -> Conversation:
    conversation = Conversation()
    conversation.messages = messages
    return conversation


def _database(directory: Path) -> Path:
    return directory.parent.parent / "session-store.db"


def _from_turns(directory: Path) -> Conversation:
    database = _database(directory)
    messages: list[dict] = []
    if database.is_file():
        connection = sqlite3.connect(sqlite_uri(database), uri=True)
        try:
            rows = connection.execute(
                "SELECT user_message, assistant_response FROM turns "
                "WHERE session_id = ? ORDER BY turn_index",
                (directory.name,),
            ).fetchall()
        finally:
            connection.close()
        for user_message, assistant in rows:
            user_text = user_message.strip() if isinstance(user_message, str) else ""
            assistant_text = assistant.strip() if isinstance(assistant, str) else ""
            if user_text:
                messages.append({"role": "user", "content": [{"type": "text", "text": user_text}]})
            if assistant_text:
                messages.append(
                    {"role": "assistant", "content": [{"type": "text", "text": assistant_text}]}
                )
    return _conversation(messages)


def _turn_prompts(directory: Path) -> list[str]:
    return [
        part["text"]
        for message in _from_turns(directory).messages
        if message.get("role") == "user"
        for part in message.get("content") or []
        if isinstance(part, dict) and part.get("type") == "text" and part.get("text")
    ]


def _from_events(path: Path) -> tuple[list[dict], list[str]]:
    messages: list[dict] = []
    prompts: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        kind = obj.get("type")
        data = obj.get("data") if isinstance(obj.get("data"), dict) else {}
        if kind == "user.message":
            text = _event_text(data.get("content"))
            if text:
                messages.append({"role": "user", "content": [{"type": "text", "text": text}]})
                prompts.append(text)
        elif kind == "system.message":
            text = _event_text(data.get("content"))
            if text:
                messages.append({"role": "system", "content": [{"type": "text", "text": text}]})
        elif kind == "assistant.message":
            content: list[dict] = []
            text = _event_text(data.get("content"))
            if text:
                content.append({"type": "text", "text": text})
            reasoning = data.get("reasoningText")
            if isinstance(reasoning, str) and reasoning.strip():
                content.append({"type": "reasoning", "text": reasoning})
            if content:
                messages.append({"role": "assistant", "content": content})
        elif kind == "tool.execution_start":
            messages.append({"role": "assistant", "content": [_tool_call(data)]})
        elif kind == "tool.execution_complete":
            result = data.get("result")
            if result is None or result == "":
                continue
            messages.append(
                {"role": "tool", "content": [{"type": "tool-result", "result": result}]}
            )
    return messages, prompts


def _event_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str) and item.strip():
                parts.append(item.strip())
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        return "\n\n".join(parts)
    return ""


def _tool_call(data: dict) -> dict:
    name = data.get("toolName")
    args = data.get("arguments") if isinstance(data.get("arguments"), dict) else {}
    if name == "view":
        return {"type": "tool-call", "toolName": "Read", "args": {"path": str(args.get("path") or "")}}
    if name == "glob":
        return {
            "type": "tool-call",
            "toolName": "Glob",
            "args": {"glob_pattern": str(args.get("pattern") or "")},
        }
    if name == "powershell":
        return {
            "type": "tool-call",
            "toolName": "Shell",
            "args": {"description": str(args.get("description") or "")},
        }
    if name == "grep":
        return {
            "type": "tool-call",
            "toolName": "Grep",
            "args": {"pattern": str(args.get("pattern") or "")},
        }
    if name == "create":
        return {
            "type": "tool-call",
            "toolName": "Create",
            "args": {"path": str(args.get("path") or "")},
        }
    return {"type": "tool-call", "toolName": str(name or "tool"), "args": args}
