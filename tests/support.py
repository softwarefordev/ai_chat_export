"""Synthetic chat stores for tests. These are not real sessions."""

from __future__ import annotations

import binascii
import hashlib
import json
import sqlite3
from pathlib import Path

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_chat(
    root: Path,
    *,
    chat_id: str,
    cwd: str,
    title: str | None = "Sample",
    updated_ms: int = 0,
    messages: list[dict] | None = None,
    prompts: list[str] | None = None,
    schema: int = 1,
    with_store: bool = True,
    raw_meta: bytes | None = None,
    loose_blobs: list[bytes] | None = None,
    child_blobs: list[bytes] | None = None,
    include_title: bool = True,
) -> Path:
    chat_dir = root / "workspace" / chat_id
    chat_dir.mkdir(parents=True, exist_ok=True)
    if raw_meta is not None:
        (chat_dir / "meta.json").write_bytes(raw_meta)
    else:
        payload: dict = {
            "schemaVersion": schema,
            "cwd": cwd,
            "updatedAtMs": updated_ms,
            "hasConversation": bool(messages),
        }
        if include_title and title is not None:
            payload["title"] = title
        (chat_dir / "meta.json").write_text(json.dumps(payload), encoding="utf-8")
    if prompts is not None:
        (chat_dir / "prompt_history.json").write_text(json.dumps(prompts), encoding="utf-8")
    if with_store and messages is not None:
        write_db(
            chat_dir / "store.db",
            messages,
            loose_blobs or [],
            child_blobs or [],
        )
    return chat_dir


def write_db(
    path: Path,
    messages: list[dict],
    loose_blobs: list[bytes],
    child_blobs: list[bytes],
) -> None:
    blobs: dict[str, bytes] = {}
    message_ids: list[str] = []
    for message in messages:
        data = json.dumps(message, separators=(",", ":")).encode("utf-8")
        message_id = digest(data)
        blobs[message_id] = data
        message_ids.append(message_id)
    extra_ids: list[str] = []
    for data in child_blobs:
        extra_id = digest(data)
        blobs[extra_id] = data
        extra_ids.append(extra_id)
    for data in loose_blobs:
        blobs[digest(data)] = data
    checkpoint = b"".join(bytes.fromhex(message_id) for message_id in message_ids)
    checkpoint_id = digest(checkpoint)
    blobs[checkpoint_id] = checkpoint
    root_blob = b"".join(
        bytes.fromhex(blob_id) for blob_id in message_ids + extra_ids + [checkpoint_id]
    )
    root_id = digest(root_blob)
    blobs[root_id] = root_blob
    meta = binascii.hexlify(json.dumps({"latestRootBlobId": root_id}).encode("utf-8")).decode("ascii")
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE blobs (id TEXT PRIMARY KEY, data BLOB)")
    connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    connection.executemany("INSERT INTO blobs (id, data) VALUES (?, ?)", blobs.items())
    connection.execute("INSERT INTO meta (key, value) VALUES (?, ?)", ("0", meta))
    connection.commit()
    connection.close()


def write_protobuf_db(
    path: Path,
    *,
    checkpoints: list[tuple[list[dict], bytes]],
    live: list[dict],
    side_blobs: list[tuple[int, bytes]] | None = None,
    unknown_live: list[bytes] | None = None,
) -> dict[str, list[str]]:
    """Build a protobuf root. Checkpoints are field 13, side blobs use the given field number."""
    blobs: dict[str, bytes] = {}
    checkpoint_ids: list[str] = []
    for messages, summary in checkpoints:
        message_ids = []
        for message in messages:
            data = json.dumps(message, separators=(",", ":")).encode("utf-8")
            message_id = digest(data)
            blobs[message_id] = data
            message_ids.append(message_id)
        checkpoint = b"".join(_protobuf_id(1, message_id) for message_id in message_ids)
        checkpoint += b"\x12" + _varint(len(summary)) + summary
        checkpoint_id = digest(checkpoint)
        blobs[checkpoint_id] = checkpoint
        checkpoint_ids.append(checkpoint_id)
    live_ids: list[str] = []
    for message in live:
        data = json.dumps(message, separators=(",", ":")).encode("utf-8")
        message_id = digest(data)
        blobs[message_id] = data
        live_ids.append(message_id)
    unknown_ids: list[str] = []
    for data in unknown_live or []:
        unknown_id = digest(data)
        blobs[unknown_id] = data
        unknown_ids.append(unknown_id)
    side_ids: list[str] = []
    side_parts: list[bytes] = []
    for field_number, data in side_blobs or []:
        side_id = digest(data)
        blobs[side_id] = data
        side_ids.append(side_id)
        side_parts.append(_protobuf_id(field_number, side_id))
    root_blob = b"".join(
        [_protobuf_id(1, blob_id) for blob_id in live_ids + unknown_ids]
        + side_parts
        + [_protobuf_id(13, blob_id) for blob_id in checkpoint_ids]
    )
    root_id = digest(root_blob)
    blobs[root_id] = root_blob
    meta = binascii.hexlify(json.dumps({"latestRootBlobId": root_id}).encode("utf-8")).decode("ascii")
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE blobs (id TEXT PRIMARY KEY, data BLOB)")
    connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    connection.executemany("INSERT INTO blobs (id, data) VALUES (?, ?)", blobs.items())
    connection.execute("INSERT INTO meta (key, value) VALUES (?, ?)", ("0", meta))
    connection.commit()
    connection.close()
    return {
        "checkpoint_ids": checkpoint_ids,
        "side_ids": side_ids,
        "unknown_ids": unknown_ids,
    }


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        bits = value & 0x7F
        value >>= 7
        if value:
            out.append(bits | 0x80)
        else:
            out.append(bits)
            return bytes(out)


def _protobuf_id(field_number: int, blob_id: str) -> bytes:
    tag = (field_number << 3) | 2
    raw = bytes.fromhex(blob_id)
    return _varint(tag) + _varint(len(raw)) + raw


def sample_messages() -> tuple[list[dict], list[str]]:
    typed = "Please add a river tool."
    messages = [
        {"role": "system", "content": "SYSTEM_PROMPT_TEXT"},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "INJECTED_CONTEXT_BLOCK"},
                {"type": "text", "text": typed},
            ],
        },
        {
            "role": "assistant",
            "content": [
                {"type": "reasoning", "text": "REASONING_PRIVATE"},
                {"type": "text", "text": "The river tool lives in tools/river.py."},
                {"type": "tool-call", "toolName": "Read", "args": {"path": "tools/river.py"}},
                {"type": "tool-call", "toolName": "Glob", "args": {"glob_pattern": "*.py"}},
                {
                    "type": "tool-call",
                    "toolName": "Shell",
                    "args": {"command": "SECRET_COMMAND_XYZ", "description": "List map tool modules"},
                },
            ],
        },
        {
            "role": "tool",
            "content": [{"type": "tool-result", "toolName": "Shell", "result": "TOOL_RESULT_PAYLOAD"}],
        },
    ]
    return messages, [typed]
