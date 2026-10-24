"""File-name stems shared by the CLI and the picker."""

from __future__ import annotations

_ILLEGAL = '<>:"/\\|?*'
_RESERVED = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{number}" for number in range(1, 10)),
        *(f"LPT{number}" for number in range(1, 10)),
    }
)
_RESERVED_FOLDED = frozenset(name.casefold() for name in _RESERVED)


def clean_stem(raw: str) -> str:
    cleaned = []
    for character in raw:
        if character in _ILLEGAL or ord(character) < 32:
            cleaned.append(" ")
        else:
            cleaned.append(character)
    return " ".join("".join(cleaned).split()).rstrip(" .")[:80]


def export_stem(title: str | None, chat_id: str) -> str:
    stem = clean_stem((title or "").strip())
    if stem and stem.casefold() not in _RESERVED_FOLDED:
        return stem
    return _fallback(chat_id)


def _fallback(chat_id: str) -> str:
    cleaned = clean_stem(chat_id)
    if not cleaned:
        return "export"
    if cleaned.casefold() in _RESERVED_FOLDED:
        return f"{cleaned}-export"
    return cleaned
