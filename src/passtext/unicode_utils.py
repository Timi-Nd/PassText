"""Unicode and UTF-8 validation helpers."""

from __future__ import annotations

import unicodedata

from .exceptions import InvalidUnicodeError


def validate_utf8_text(value: str) -> None:
    """Reject values that cannot be represented as legal UTF-8."""

    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:  # pragma: no cover - defensive branch
        raise InvalidUnicodeError("input cannot be encoded as valid UTF-8") from exc


def codepoint_count(value: str) -> int:
    """Return the number of Unicode code points in the string."""

    return len(value)


def utf8_byte_count(value: str) -> int:
    """Return the number of bytes produced by encoding to UTF-8."""

    validate_utf8_text(value)
    return len(value.encode("utf-8", errors="strict"))


def contains_non_ascii(value: str) -> bool:
    """Return whether the string contains any non-ASCII code points."""

    return any(ord(ch) > 127 for ch in value)


def normalize_for_config(value: str, normalization: str) -> str:
    """Apply the configured normalization mode without altering the original."""

    if normalization == "none":
        return value
    if normalization == "nfc":
        return unicodedata.normalize("NFC", value)
    raise ValueError(f"unsupported normalization mode: {normalization}")
