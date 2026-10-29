"""Input validation and process orchestration for PassText."""

from __future__ import annotations

from .config import PassTextConfig
from .exceptions import (
    InvalidInputTypeError,
    InvalidUnicodeError,
    ProcessingFailureError,
    ProcessingLimitError,
)
from .metadata import TextMetadata
from .normalization import apply_normalization
from .representation import PreparedPassword
from .unicode_utils import codepoint_count, contains_non_ascii, utf8_byte_count, validate_utf8_text


def validate_password_input(password: object, config: PassTextConfig) -> str:
    """Validate the raw password input and return it as a string.

    Empty strings are valid inputs; they produce valid metadata without modification.
    """

    if not isinstance(password, str):
        raise InvalidInputTypeError("password must be a str instance")

    try:
        validate_utf8_text(password)
    except InvalidUnicodeError as exc:
        raise InvalidUnicodeError("password contains invalid UTF-8 content") from exc

    if len(password) > config.max_codepoints:
        raise ProcessingLimitError(
            "password exceeds configured maximum Unicode code-point count"
        )

    if utf8_byte_count(password) > config.max_utf8_bytes:
        raise ProcessingLimitError("password exceeds configured maximum UTF-8 byte count")

    return password


def build_metadata(original: str, processed: str, config: PassTextConfig) -> TextMetadata:
    """Create safe metadata without exposing any password content."""

    original_codepoints = codepoint_count(original)
    processed_codepoints = codepoint_count(processed)

    try:
        original_utf8_bytes = utf8_byte_count(original)
        processed_utf8_bytes = utf8_byte_count(processed)
    except UnicodeError as exc:
        raise ProcessingFailureError("metadata calculation encountered invalid Unicode") from exc

    return TextMetadata(
        original_codepoints=original_codepoints,
        original_utf8_bytes=original_utf8_bytes,
        processed_codepoints=processed_codepoints,
        processed_utf8_bytes=processed_utf8_bytes,
        contains_non_ascii=contains_non_ascii(original),
        normalization=config.normalization,
        normalization_changed=(processed != original),
    )


def process_password(password: object, config: PassTextConfig | None = None) -> PreparedPassword:
    """Process one password value and return a prepared representation.

    This is the public API entry point for PassText.
    """

    if config is None:
        config = PassTextConfig()

    validated = validate_password_input(password, config)
    processed = apply_normalization(validated, config.normalization)

    # Enforce processing limits on the processed value as well. This ensures the pipeline
    # remains safe even when a normalization step expands the representation.
    if codepoint_count(processed) > config.max_codepoints:
        raise ProcessingLimitError(
            "processed password exceeds configured maximum Unicode code-point count"
        )
    if utf8_byte_count(processed) > config.max_utf8_bytes:
        raise ProcessingLimitError(
            "processed password exceeds configured maximum UTF-8 byte count"
        )

    metadata = build_metadata(validated, processed, config)

    from .representation import PreparedPassword

    return PreparedPassword(
        original_text=validated,
        processed_text=processed,
        metadata=metadata,
        config=config,
    )
