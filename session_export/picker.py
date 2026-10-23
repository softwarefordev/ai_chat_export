"""Terminal picker for choosing a chat to export."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from session_export.catalog import Chat, filter_workspace


@dataclass(frozen=True)
class PickerResult:
    chat_id: str | None
    delete_requested: bool = False


def run_picker(chats: list[Chat], theme: str, keys, launch_dir: str, write, rows: int = 20) -> PickerResult:
    scope = "all"
    selected = 0

    def visible() -> list[Chat]:
        if scope == "workspace":
            return filter_workspace(chats, launch_dir)
        return list(chats)

    def paint() -> None:
        nonlocal selected
        shown = visible()
        if shown:
            selected = min(selected, len(shown) - 1)
        else:
            selected = 0
        write(render_frame(shown, selected, scope, theme, rows))

    paint()
    for key in keys:
        shown = visible()
        if key == "up" and shown:
            selected = max(0, selected - 1)
        elif key == "down" and shown:
            selected = min(len(shown) - 1, selected + 1)
        elif key in ("left", "right"):
            scope = "workspace" if scope == "all" else "all"
            selected = 0
        elif key == "backspace":
            pass
        elif key == "esc":
            paint()
            return PickerResult(None, False)
        elif key == "enter":
            paint()
            shown = visible()
            if not shown:
                return PickerResult(None, False)
            return PickerResult(shown[selected].id, False)
        else:
            continue
        paint()
    return PickerResult(None, False)


def render_frame(chats: list[Chat], selected: int, scope: str, theme: str, rows: int = 20) -> str:
    if scope == "all":
        header = "All chats *    This workspace"
    else:
        header = "All chats    This workspace *"
    lines = [header]
    start = 0
    if chats and len(chats) > rows:
        start = min(max(0, selected - rows // 2), len(chats) - rows)
    window = chats[start : start + rows]
    if not window:
        lines.append("(no chats)")
    for offset, chat in enumerate(window):
        marker = ">" if start + offset == selected else " "
        lines.append(
            f"{marker} {chat.display_title}    {chat.workspace_name}    {chat.updated_label}"
        )
    count = len(chats)
    index = (selected + 1) if count else 0
    lines.append(
        f"{index}/{count}  up/down move  left/right scope  Enter exports  Esc closes"
    )
    lines.append(f"theme: {theme}")
    return "\n".join(lines) + "\n"


def call_with_restore(body, teardown, setup=None):
    if setup is not None:
        setup()
    try:
        return body()
    finally:
        teardown()


def setup_terminal():
    if os.name == "nt":
        return None
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    tty.setcbreak(descriptor)
    return saved


def teardown_terminal(saved) -> None:
    if saved is None or os.name == "nt":
        return
    import termios

    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved)


def read_key():
    if os.name == "nt":
        import msvcrt

        character = msvcrt.getwch()
        if character in ("\x00", "\xe0"):
            arrows = {"H": "up", "P": "down", "K": "left", "M": "right"}
            return arrows.get(msvcrt.getwch(), "")
        if character == "\r":
            return "enter"
        if character == "\x1b":
            return "esc"
        if character == "\x08":
            return "backspace"
        if character == "\x03":
            raise KeyboardInterrupt
        return ""
    character = sys.stdin.read(1)
    if character == "\x03":
        raise KeyboardInterrupt
    if character in ("\r", "\n"):
        return "enter"
    if character in ("\x7f", "\x08"):
        return "backspace"
    if character == "\x1b":
        following = sys.stdin.read(2)
        arrows = {"[A": "up", "[B": "down", "[D": "left", "[C": "right"}
        return arrows.get(following, "")
    return ""
