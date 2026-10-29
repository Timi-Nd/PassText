"""Configuration for PassText processing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .exceptions import InvalidConfigurationError

NormalizationMode = Literal["none", "nfc"]


@dataclass(frozen=True)
class PassTextConfig:
    """Immutable processing configuration.

    The defaults are intentionally conservative and suitable for password processing in
    interactive or batch contexts.
    """

    max_utf8_bytes: int = 4096
    max_codepoints: int = 1024
    normalization: NormalizationMode = "none"

    def __post_init__(self) -> None:
        if not isinstance(self.max_utf8_bytes, int):
            raise InvalidConfigurationError("max_utf8_bytes must be an integer")
        if self.max_utf8_bytes <= 0:
            raise InvalidConfigurationError("max_utf8_bytes must be greater than zero")

        if not isinstance(self.max_codepoints, int):
            raise InvalidConfigurationError("max_codepoints must be an integer")
        if self.max_codepoints <= 0:
            raise InvalidConfigurationError("max_codepoints must be greater than zero")

        if self.normalization not in {"none", "nfc"}:
            raise InvalidConfigurationError("normalization must be 'none' or 'nfc'")
