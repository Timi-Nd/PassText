"""Prepared password representation for downstream processing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import PassTextConfig
from .metadata import TextMetadata


@dataclass(frozen=True, slots=True)
class PreparedPassword:
    """Internal representation exposing only safe metadata and controlled access.

    Password contents are intentionally not printed by this object's repr().
    """

    original_text: str
    processed_text: str
    metadata: TextMetadata
    config: PassTextConfig

    def __repr__(self) -> str:
        return (
            "PreparedPassword("
            f"original_codepoints={self.metadata.original_codepoints}, "
            f"processed_codepoints={self.metadata.processed_codepoints}, "
            f"normalization={self.metadata.normalization!r}, "
            f"normalization_changed={self.metadata.normalization_changed!r})"
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a safe dictionary representation without including the password."""

        return {
            "original_codepoints": self.metadata.original_codepoints,
            "processed_codepoints": self.metadata.processed_codepoints,
            "contains_non_ascii": self.metadata.contains_non_ascii,
            "normalization": self.metadata.normalization,
            "normalization_changed": self.metadata.normalization_changed,
        }
