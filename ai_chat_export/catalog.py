"""Read the local agent chat catalog."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SessionSource:
    id: str
    argument: str
    filter_label: str
    column: str


SESSION_SOURCES: tuple[SessionSource, ...] = (
    SessionSource("cli", "cursor-cli", "Cursor-CLI", "Cu-CLI"),
    SessionSource("ide", "cursor-ide", "Cursor-IDE", "Cu-IDE"),
)


def column_label(source_id: str) -> str:
    for item in SESSION_SOURCES:
        if item.id == source_id:
            return item.column
    return source_id


def allowed_sources(arguments: list[str] | None) -> set[str] | None:
    if not arguments:
        return None
    chosen = {item.id for item in SESSION_SOURCES if item.argument in arguments}
    if {item.id for item in SESSION_SOURCES} <= chosen:
        return None
    return chosen


@dataclass(frozen=True)
class Chat:
    id: str
    title: str | None
    cwd: str
    workspace_name: str
    updated_at_ms: int
    has_store: bool
    path: Path
    source: str = "cli"

    @property
    def display_title(self) -> str:
        if self.title:
            return self.title
        return self.id

    @property
    def updated_label(self) -> str:
        return format_timestamp(self.updated_at_ms)

    @property
    def source_label(self) -> str:
        return column_label(self.source)


def format_timestamp(updated_at_ms: int) -> str:
    return format_datetime(datetime.fromtimestamp(updated_at_ms / 1000))


def format_datetime(moment: datetime) -> str:
    hour = moment.hour % 12 or 12
    suffix = "AM" if moment.hour < 12 else "PM"
    return (
        f"{moment.strftime('%b')} {moment.day}, {moment.year} "
        f"{hour:02d}:{moment.minute:02d} {suffix}"
    )


def normalize_dir(path: str) -> str:
    normalized = os.path.normpath(os.path.abspath(path))
    if sys.platform == "win32":
        return os.path.normcase(normalized)
    return normalized


def same_directory(left: str, right: str) -> bool:
    if not left or not right:
        return False
    return normalize_dir(left) == normalize_dir(right)


def workspace_folder(cwd: str) -> str:
    name = Path(cwd).name
    if name:
        return name
    return cwd


def load_catalog(root: Path, warnings: list[str] | None = None) -> list[Chat]:
    notes = warnings if warnings is not None else []
    chats: list[Chat] = []
    root = Path(root)
    if not root.is_dir():
        return []
    for meta_path in root.glob("*/*/meta.json"):
        chat_dir = meta_path.parent
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            notes.append(f"Unreadable metadata for {chat_dir.name}: {exc}")
            continue
        if not isinstance(payload, dict):
            notes.append(f"Unreadable metadata for {chat_dir.name}: not an object")
            continue
        version = payload.get("schemaVersion")
        if version != 1:
            notes.append(f"Unsupported schemaVersion {version} for {chat_dir.name}")
            continue
        cwd = payload.get("cwd") or ""
        if not isinstance(cwd, str):
            cwd = str(cwd)
        title = payload.get("title")
        if not isinstance(title, str) or not title:
            title = None
        try:
            updated_ms = int(payload.get("updatedAtMs") or 0)
        except (TypeError, ValueError):
            updated_ms = 0
        chats.append(
            Chat(
                id=chat_dir.name,
                title=title,
                cwd=cwd,
                workspace_name=workspace_folder(cwd) if cwd else "",
                updated_at_ms=updated_ms,
                has_store=(chat_dir / "store.db").is_file(),
                path=chat_dir,
            )
        )
    chats.sort(key=lambda chat: (chat.updated_at_ms, chat.id), reverse=True)
    return chats


def filter_workspace(chats: list[Chat], launch_dir: str) -> list[Chat]:
    return [chat for chat in chats if same_directory(chat.cwd, launch_dir)]
