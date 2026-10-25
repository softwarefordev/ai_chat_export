"""Read GitHub Copilot IDE sessions."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from ai_chat_export.catalog import Chat, workspace_folder
from ai_chat_export.copilot import load_copilot_conversation, session_from_events
from ai_chat_export.store import Conversation, sqlite_uri


def vscode_user_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
        return base / "Code" / "User"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Code" / "User"
    return Path.home() / ".config" / "Code" / "User"


def load_vscode_catalog(
    root: Path,
    warnings: list[str] | None = None,
    include_empty: bool = False,
) -> list[Chat]:
    notes = warnings if warnings is not None else []
    root = Path(root)
    if not root.is_dir():
        return []
    found: list[tuple[Path, Path | None]] = []
    storage = root / "workspaceStorage"
    if storage.is_dir():
        for workspace in storage.iterdir():
            sessions = workspace / "chatSessions"
            if not sessions.is_dir():
                continue
            for path in sessions.iterdir():
                if _session_file(path):
                    found.append((path, workspace / "workspace.json"))
    empty = root / "globalStorage" / "emptyWindowChatSessions"
    if empty.is_dir():
        for path in empty.iterdir():
            if _session_file(path):
                found.append((path, None))
    rows: list[Chat] = []
    for path, workspace_json in found:
        chat = _vscode_chat(path, workspace_json, notes, include_empty)
        if chat is not None:
            rows.append(chat)
    return rows


def _session_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in {".json", ".jsonl"}


def _vscode_chat(
    path: Path,
    workspace_json: Path | None,
    notes: list[str],
    include_empty: bool,
) -> Chat | None:
    try:
        document = _document(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        notes.append(f"Unreadable Copilot IDE session {path.stem}: {exc}")
        return None
    if not isinstance(document, dict):
        notes.append(f"Unreadable Copilot IDE session {path.stem}: not an object")
        return None
    first_line, has_turn = _turn_summary(document)
    if not has_turn and not include_empty:
        return None
    session_id = document.get("sessionId")
    if not isinstance(session_id, str) or not session_id:
        session_id = path.stem
    cwd = _workspace_cwd(workspace_json)
    return Chat(
        id=session_id,
        title=_title(document.get("customTitle"), first_line),
        cwd=cwd,
        workspace_name=workspace_folder(cwd) if cwd else "",
        updated_at_ms=_updated_ms(document),
        has_store=has_turn,
        path=path,
        source="cp-ide",
    )


def _document(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                continue
            if item.get("kind") == 0 and isinstance(item.get("v"), dict):
                return item["v"]
        return {}
    document = json.loads(text)
    if isinstance(document, dict) and document.get("kind") == 0 and isinstance(document.get("v"), dict):
        return document["v"]
    if not isinstance(document, dict):
        raise ValueError("not an object")
    return document


def _turn_summary(document: dict) -> tuple[str, bool]:
    requests = document.get("requests")
    if not isinstance(requests, list):
        return "", False
    first_line = ""
    has_turn = False
    for request in requests:
        if not isinstance(request, dict):
            continue
        message = request.get("message")
        text = ""
        if isinstance(message, dict) and isinstance(message.get("text"), str):
            text = message["text"].strip()
        if text:
            has_turn = True
            if not first_line:
                first_line = text.splitlines()[0].strip()
        response = request.get("response")
        if not isinstance(response, list):
            continue
        for part in response:
            if isinstance(part, dict) and isinstance(part.get("value"), str) and part["value"].strip():
                has_turn = True
    return first_line, has_turn


def _title(custom: object, first_line: str) -> str | None:
    if isinstance(custom, str) and custom.strip():
        return custom.strip()
    if first_line:
        return first_line
    return None


def _updated_ms(document: dict) -> int:
    latest = _millis(document.get("lastMessageDate"))
    if latest is not None:
        return latest
    created = _millis(document.get("creationDate"))
    if created is not None:
        return created
    return 0


def _millis(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(value)


def _workspace_cwd(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ""
    if not isinstance(document, dict):
        return ""
    folder = document.get("folder")
    if not isinstance(folder, str):
        return ""
    return _file_uri_path(folder)


def _file_uri_path(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "file":
        return ""
    path = unquote(parsed.path)
    if re.match(r"^/[A-Za-z]:", path):
        path = path[1:]
    return path


def github_copilot_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        return base / "github-copilot"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "github-copilot"
    return Path.home() / ".config" / "github-copilot"


def load_vscode_agent_sessions(
    vscode_root: Path,
    events_root: Path,
    warnings: list[str] | None = None,
    include_empty: bool = False,
) -> list[Chat]:
    notes = warnings if warnings is not None else []
    database = Path(vscode_root) / "globalStorage" / "agent-host.db"
    if not database.is_file():
        return []
    try:
        connection = sqlite3.connect(sqlite_uri(database), uri=True)
        try:
            stored = connection.execute(
                "SELECT provider_data, metadata, tombstoned FROM chats_v2"
            ).fetchall()
        finally:
            connection.close()
    except (sqlite3.Error, OSError) as exc:
        notes.append(f"Unreadable Copilot IDE session agent-host: {exc}")
        return []
    rows: list[Chat] = []
    for provider, metadata, tombstoned in stored:
        if tombstoned:
            continue
        session_id = _sdk_session_id(provider)
        if not session_id:
            continue
        chat = session_from_events(
            Path(events_root) / "session-state" / session_id,
            notes,
            source="cp-ide",
        )
        if chat is None:
            if include_empty:
                rows.append(
                    Chat(
                        id=session_id,
                        title=_summary_title(metadata),
                        cwd="",
                        workspace_name="",
                        updated_at_ms=0,
                        has_store=False,
                        path=Path(events_root) / "session-state" / session_id,
                        source="cp-ide",
                    )
                )
            continue
        title = _summary_title(metadata)
        if title is not None:
            chat = Chat(
                id=chat.id,
                title=title,
                cwd=chat.cwd,
                workspace_name=chat.workspace_name,
                updated_at_ms=chat.updated_at_ms,
                has_store=chat.has_store,
                path=chat.path,
                source=chat.source,
                time_label=chat.time_label,
            )
        rows.append(chat)
    return rows


def _sdk_session_id(provider: object) -> str:
    if not isinstance(provider, str) or not provider.strip():
        return ""
    try:
        document = json.loads(provider)
    except json.JSONDecodeError:
        return ""
    if not isinstance(document, dict):
        return ""
    session_id = document.get("sdkSessionId")
    if isinstance(session_id, str) and session_id.strip():
        return session_id.strip()
    return ""


def _summary_title(metadata: object) -> str | None:
    if not isinstance(metadata, str) or not metadata.strip():
        return None
    try:
        document = json.loads(metadata)
    except json.JSONDecodeError:
        return None
    if not isinstance(document, dict):
        return None
    data = document.get("data")
    if not isinstance(data, dict):
        return None
    summary = data.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()
    return None


def load_copilot_ide_catalog(
    root: Path,
    warnings: list[str] | None = None,
    include_empty: bool = False,
    events_root: Path | None = None,
) -> list[Chat]:
    notes = warnings if warnings is not None else []
    root = Path(root)
    if not root.is_dir():
        return []
    rows: list[Chat] = []
    for path in root.rglob("copilot-agent-sessions-nitrite.db"):
        if "bg-agent-sessions" in path.parts:
            continue
        if "rd" not in path.parts and "vs" not in path.parts:
            continue
        rows.extend(_nitrite_chats(path, notes, include_empty, events_root))
    return rows


def _nitrite_chats(
    path: Path,
    notes: list[str],
    include_empty: bool,
    events_root: Path | None,
) -> list[Chat]:
    try:
        data = path.read_bytes()
    except OSError as exc:
        notes.append(f"Unreadable Copilot IDE session {path.stem}: {exc}")
        return []
    rows: list[Chat] = []
    seen: set[str] = set()
    for session in _live_sessions(_java_strings(data)) + _sessions_from_strings(_java_strings(data)):
        if session["id"] in seen:
            continue
        seen.add(session["id"])
        user_line = next((text for source, text in session["turns"] if source == "user" and text.strip()), "")
        assistant = any(source == "copilot" and text.strip() for source, text in session["turns"])
        if not user_line and not assistant:
            if not include_empty:
                continue
        if events_root is not None:
            logged = session_from_events(
                Path(events_root) / "session-state" / session["id"],
                notes,
                source="cp-ide",
            )
            if logged is not None:
                rows.append(logged)
                continue
        cwd = session["workspace"]
        updated = session["modified"] if session["modified"] is not None else (session["created"] or 0)
        rows.append(
            Chat(
                id=session["id"],
                title=user_line.splitlines()[0].strip() if user_line.strip() else None,
                cwd=cwd,
                workspace_name=workspace_folder(cwd) if cwd else "",
                updated_at_ms=updated,
                has_store=bool(user_line or assistant),
                path=path,
                source="cp-ide",
            )
        )
    return rows


def _java_strings(data: bytes) -> list[str]:
    found: list[str] = []
    index = 0
    limit = len(data)
    while index < limit - 3:
        if data[index] != 0x74:
            index += 1
            continue
        length = int.from_bytes(data[index + 1 : index + 3], "big")
        end = index + 3 + length
        if length <= 0 or length > 10000 or end > limit:
            index += 1
            continue
        try:
            text = data[index + 3 : end].decode("utf-8")
        except UnicodeDecodeError:
            index += 1
            continue
        if text.isprintable() or "\n" in text:
            found.append(text)
            index = end
            continue
        index += 1
    return found


_NITRITE_FIELDS = {"sessionId", "modifiedAt", "createdAt", "dirName", "path", "source", "value", "name"}


def _sessions_from_strings(strings: list[str]) -> list[dict]:
    sessions: list[dict] = []
    current: dict | None = None
    index = 0
    while index < len(strings):
        token = strings[index]
        if token == "sessionId" and index + 1 < len(strings) and strings[index + 1] not in _NITRITE_FIELDS:
            current = {
                "id": strings[index + 1],
                "turns": [],
                "modified": None,
                "created": None,
                "workspace": "",
            }
            sessions.append(current)
            index += 2
            continue
        if current is None:
            index += 1
            continue
        if token in {"modifiedAt", "createdAt"} and index + 1 < len(strings) and strings[index + 1].isdigit():
            current["modified" if token == "modifiedAt" else "created"] = int(strings[index + 1])
            index += 2
            continue
        if token in {"dirName", "path"} and index + 1 < len(strings) and strings[index + 1] not in _NITRITE_FIELDS:
            if token == "path" or not current["workspace"]:
                current["workspace"] = strings[index + 1]
            index += 2
            continue
        if (
            token == "source"
            and index + 3 < len(strings)
            and strings[index + 1] in {"user", "copilot"}
            and strings[index + 2] == "value"
        ):
            current["turns"].append((strings[index + 1], strings[index + 3]))
            index += 4
            continue
        index += 1
    return sessions


def _live_sessions(strings: list[str]) -> list[dict]:
    sessions: list[dict] = []
    seen: set[str] = set()
    index = 0
    while index < len(strings):
        if strings[index] == "name" and index + 2 < len(strings) and strings[index + 1] == "value":
            text = strings[index + 2]
            window = strings[index + 3 : index + 8]
            if "source" in window and "copilot" in window:
                session_id = ""
                for follow in range(index + 3, min(len(strings), index + 24)):
                    if (
                        strings[follow] == "conversationId"
                        and follow + 1 < len(strings)
                        and _uuid_like(strings[follow + 1])
                    ):
                        session_id = strings[follow + 1]
                        break
                if session_id and session_id not in seen and text.strip():
                    seen.add(session_id)
                    sessions.append(
                        {
                            "id": session_id,
                            "turns": [("user", text)],
                            "modified": None,
                            "created": None,
                            "workspace": "",
                        }
                    )
            index += 3
            continue
        index += 1
    return sessions


def _uuid_like(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value))


def load_copilot_ide_conversation(path: Path, session_id: str) -> tuple[Conversation, list[str]]:
    path = Path(path)
    if path.is_dir():
        conversation, prompts, _note = load_copilot_conversation(path)
        return conversation, prompts
    if path.suffix.lower() in {".json", ".jsonl"}:
        return _vscode_conversation(_document(path))
    for session in _sessions_from_strings(_java_strings(path.read_bytes())):
        if session["id"] == session_id:
            return _turn_conversation(session["turns"])
    return Conversation(), []


def _vscode_conversation(document: dict) -> tuple[Conversation, list[str]]:
    messages: list[dict] = []
    prompts: list[str] = []
    requests = document.get("requests")
    if not isinstance(requests, list):
        return Conversation(), []
    for request in requests:
        if not isinstance(request, dict):
            continue
        message = request.get("message")
        text = ""
        if isinstance(message, dict) and isinstance(message.get("text"), str):
            text = message["text"].strip()
        if text:
            messages.append({"role": "user", "content": [{"type": "text", "text": text}]})
            prompts.append(text)
        response = request.get("response")
        if not isinstance(response, list):
            continue
        content: list[dict] = []
        for part in response:
            if not isinstance(part, dict):
                continue
            value = part.get("value")
            if isinstance(value, str) and value.strip() and part.get("kind") is None:
                content.append({"type": "text", "text": value.strip()})
                continue
            if part.get("kind") == "toolInvocationSerialized":
                content.append(_ide_tool_call(part))
                result = part.get("result")
                if isinstance(result, str) and result.strip():
                    messages.append({"role": "assistant", "content": content})
                    content = []
                    messages.append(
                        {"role": "tool", "content": [{"type": "tool-result", "result": result}]}
                    )
        if content:
            messages.append({"role": "assistant", "content": content})
    conversation = Conversation()
    conversation.messages = messages
    return conversation, prompts


def _turn_conversation(turns: list[tuple[str, str]]) -> tuple[Conversation, list[str]]:
    messages: list[dict] = []
    prompts: list[str] = []
    for source, text in turns:
        cleaned = text.strip()
        if not cleaned:
            continue
        if source == "user":
            messages.append({"role": "user", "content": [{"type": "text", "text": cleaned}]})
            prompts.append(cleaned)
        elif source == "copilot":
            messages.append({"role": "assistant", "content": [{"type": "text", "text": cleaned}]})
    conversation = Conversation()
    conversation.messages = messages
    return conversation, prompts


def _ide_tool_call(part: dict) -> dict:
    tool_id = str(part.get("toolId") or part.get("toolName") or "tool")
    args = _tool_args(part)
    path = str(args.get("path") or "")
    if tool_id == "copilot_readFile":
        return {"type": "tool-call", "toolName": "Read", "args": {"path": path}}
    if tool_id == "copilot_createFile":
        return {"type": "tool-call", "toolName": "Create", "args": {"path": path}}
    if tool_id == "copilot_findFiles":
        pattern = args.get("glob_pattern") or args.get("pattern") or ""
        return {"type": "tool-call", "toolName": "Glob", "args": {"glob_pattern": str(pattern)}}
    if tool_id == "run_in_terminal":
        return {
            "type": "tool-call",
            "toolName": "Shell",
            "args": {"description": str(args.get("description") or "")},
        }
    if tool_id in {"copilot_replaceString", "copilot_multiReplaceString"}:
        return {"type": "tool-call", "toolName": "Edit", "args": {"path": path}}
    return {"type": "tool-call", "toolName": tool_id, "args": {}}


def _tool_args(part: dict) -> dict:
    for key in ("parameters", "input", "args"):
        value = part.get(key)
        if isinstance(value, dict):
            return value
    return {}
