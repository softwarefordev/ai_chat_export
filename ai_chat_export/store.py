"""Read one agent conversation from store.db."""

from __future__ import annotations

import binascii
import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@dataclass
class Conversation:
    messages: list[dict] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unlinked_images: list[str] = field(default_factory=list)


def sqlite_uri(path: Path) -> str:
    """Open `path` read-only. `?` and `#` stay in the path."""
    encoded = quote(Path(path).resolve().as_posix(), safe="/:")
    return f"file:{encoded}?mode=ro"


def load_conversation(db_path: Path) -> Conversation:
    connection = sqlite3.connect(sqlite_uri(db_path), uri=True)
    try:
        row = connection.execute("SELECT value FROM meta LIMIT 1").fetchone()
        if row is None:
            raise ValueError("conversation meta is missing")
        meta = json.loads(binascii.unhexlify(row[0]).decode("utf-8"))
        root_id = meta["latestRootBlobId"]
        blobs = {
            blob_id: data
            for blob_id, data in connection.execute("SELECT id, data FROM blobs")
        }
    finally:
        connection.close()

    root = blobs.get(root_id)
    if root is None:
        raise ValueError("root blob is missing")

    known = {bytes.fromhex(blob_id): blob_id for blob_id in blobs}
    conversation = Conversation()
    if _is_aligned_id_list(root, blobs):
        _load_raw(conversation, root, blobs, known, root_id)
    else:
        layout = _protobuf_layout(root, blobs)
        if layout is None:
            _load_raw(conversation, root, blobs, known, root_id)
        else:
            _load_protobuf(conversation, blobs, root_id, *layout)
    return conversation


def _load_raw(
    conversation: Conversation,
    root: bytes,
    blobs: dict[str, bytes],
    known: dict[bytes, str],
    root_id: str,
) -> None:
    seen: set[str] = set()
    children: list[tuple[str, bytes | None]] = []
    for child_id in _ordered_ids(root, known):
        if child_id in seen or child_id == root_id:
            continue
        seen.add(child_id)
        children.append((child_id, blobs.get(child_id)))

    pending: list[tuple[str, bytes | None]] = []
    message_ids: set[str] = set()
    for child_id, data in children:
        message = _role_message(data) if data else None
        if message is None:
            pending.append((child_id, data))
            continue
        conversation.messages.append(message)
        message_ids.add(child_id)

    for child_id, data in pending:
        if data is None:
            conversation.skipped.append(child_id)
        elif _is_repeat_index(data, message_ids) or _checkpoint_message_ids(data, blobs):
            continue
        elif data.startswith(PNG_MAGIC):
            conversation.unlinked_images.append(child_id)
        else:
            conversation.skipped.append(child_id)
    _add_unlinked_images(conversation, blobs, seen)


def _load_protobuf(
    conversation: Conversation,
    blobs: dict[str, bytes],
    root_id: str,
    live_ids: list[str],
    checkpoint_ids: list[str],
) -> None:
    seen: set[str] = set()
    for checkpoint_id in checkpoint_ids:
        for message_id in _checkpoint_message_ids(blobs.get(checkpoint_id), blobs) or []:
            _append_message(conversation, blobs, message_id, seen)
    for child_id in live_ids:
        if child_id == root_id:
            continue
        data = blobs.get(child_id)
        if _append_message(conversation, blobs, child_id, seen):
            continue
        if data is not None and _checkpoint_message_ids(data, blobs):
            continue
        if data is not None and data.startswith(PNG_MAGIC):
            conversation.unlinked_images.append(child_id)
            continue
        conversation.skipped.append(child_id)
    _add_unlinked_images(conversation, blobs, seen | set(checkpoint_ids) | set(live_ids))


def _append_message(
    conversation: Conversation,
    blobs: dict[str, bytes],
    message_id: str,
    seen: set[str],
) -> bool:
    if message_id in seen:
        return True
    message = _role_message(blobs.get(message_id))
    if message is None:
        return False
    seen.add(message_id)
    conversation.messages.append(message)
    return True


def _add_unlinked_images(
    conversation: Conversation,
    blobs: dict[str, bytes],
    seen: set[str],
) -> None:
    referenced = {blob_id for blob_id in seen}
    for message in conversation.messages:
        encoded = json.dumps(message)
        for blob_id in blobs:
            if blob_id in encoded:
                referenced.add(blob_id)
    for blob_id, data in blobs.items():
        if not data.startswith(PNG_MAGIC):
            continue
        if blob_id in referenced or blob_id in seen:
            continue
        conversation.unlinked_images.append(blob_id)


def _is_aligned_id_list(blob: bytes, blobs: dict[str, bytes]) -> bool:
    if len(blob) < 32 or len(blob) % 32 != 0:
        return False
    return all(blob[index : index + 32].hex() in blobs for index in range(0, len(blob), 32))


def _protobuf_layout(root: bytes, blobs: dict[str, bytes]) -> tuple[list[str], list[str]] | None:
    fields = _protobuf_fields(root)
    if fields is None:
        return None
    live: list[str] = []
    checkpoints: list[str] = []
    for field_number, value in fields:
        if not isinstance(value, bytes) or len(value) != 32:
            continue
        blob_id = value.hex()
        if blob_id not in blobs:
            continue
        if field_number == 1:
            live.append(blob_id)
        elif _checkpoint_message_ids(blobs[blob_id], blobs):
            checkpoints.append(blob_id)
    if not any(_role_message(blobs.get(blob_id)) for blob_id in live):
        return None
    return live, checkpoints


def _checkpoint_message_ids(data: bytes | None, blobs: dict[str, bytes]) -> list[str] | None:
    if not data or _role_message(data):
        return None
    if len(data) % 32 == 0:
        raw_ids = [data[index : index + 32].hex() for index in range(0, len(data), 32)]
        if raw_ids and all(_role_message(blobs.get(blob_id)) for blob_id in raw_ids):
            return raw_ids
    fields = _protobuf_fields(data)
    if fields is None:
        return None
    message_ids = [
        value.hex()
        for field_number, value in fields
        if field_number == 1 and isinstance(value, bytes) and len(value) == 32 and value.hex() in blobs
    ]
    if not message_ids or any(_role_message(blobs.get(blob_id)) is None for blob_id in message_ids):
        return None
    return message_ids


def _protobuf_fields(data: bytes) -> list[tuple[int, int | bytes]] | None:
    if not data:
        return None
    fields: list[tuple[int, int | bytes]] = []
    index = 0
    try:
        while index < len(data):
            key, index = _read_varint(data, index)
            field_number, wire = key >> 3, key & 7
            if field_number == 0 or field_number > 200:
                return None
            if wire == 0:
                value, index = _read_varint(data, index)
                fields.append((field_number, value))
            elif wire == 2:
                length, index = _read_varint(data, index)
                if length < 0 or index + length > len(data):
                    return None
                fields.append((field_number, data[index : index + length]))
                index += length
            elif wire == 1:
                if index + 8 > len(data):
                    return None
                index += 8
            elif wire == 5:
                if index + 4 > len(data):
                    return None
                index += 4
            else:
                return None
    except (ValueError, IndexError):
        return None
    if index != len(data):
        return None
    return fields


def _read_varint(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while index < len(data) and shift <= 63:
        byte = data[index]
        index += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, index
        shift += 7
    raise ValueError("bad varint")


def _ordered_ids(blob: bytes, known: dict[bytes, str]) -> list[str]:
    found: list[str] = []
    index = 0
    limit = len(blob) - 31
    while index < limit:
        chunk = blob[index : index + 32]
        blob_id = known.get(chunk)
        if blob_id is None:
            index += 1
            continue
        found.append(blob_id)
        index += 32
    return found


def _is_repeat_index(data: bytes, message_ids: set[str]) -> bool:
    if not message_ids or len(data) % 32 != 0:
        return False
    for offset in range(0, len(data), 32):
        if data[offset : offset + 32].hex() not in message_ids:
            return False
    return True


def _role_message(data: bytes | None) -> dict | None:
    if not data or data[:1] not in (b"{", b"["):
        return None
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict) and isinstance(payload.get("role"), str):
        return payload
    return None
