import pytest

from passtext import (
    InvalidConfigurationError,
    InvalidInputTypeError,
    InvalidUnicodeError,
    PassTextConfig,
    ProcessingLimitError,
    process_password,
)


def test_empty_password_is_valid():
    result = process_password("", config=PassTextConfig())
    assert result.original_text == ""
    assert result.processed_text == ""
    assert result.metadata.original_codepoints == 0
    assert result.metadata.processed_codepoints == 0
    assert result.metadata.original_utf8_bytes == 0
    assert result.metadata.processed_utf8_bytes == 0


def test_rejects_non_string_input():
    with pytest.raises(InvalidInputTypeError):
        process_password(123, config=PassTextConfig())


def test_rejects_surrogate_code_points():
    with pytest.raises(InvalidUnicodeError):
        process_password("\ud800", config=PassTextConfig())


def test_rejects_input_over_codepoint_limit():
    config = PassTextConfig(max_codepoints=2)
    with pytest.raises(ProcessingLimitError):
        process_password("abc", config=config)


def test_rejects_input_over_utf8_limit():
    config = PassTextConfig(max_utf8_bytes=3)
    with pytest.raises(ProcessingLimitError):
        process_password("éé", config=config)


def test_unicode_codepoint_and_utf8_counts():
    result = process_password("éA🙂", config=PassTextConfig())
    assert result.metadata.original_codepoints == 3
    assert result.metadata.original_utf8_bytes == 7
    assert result.metadata.processed_codepoints == 3
    assert result.metadata.processed_utf8_bytes == 7
    assert result.metadata.contains_non_ascii is True


def test_nfc_normalization_changes_processed_text():
    result = process_password("e\u0301", config=PassTextConfig(normalization="nfc"))
    assert result.original_text == "e\u0301"
    assert result.processed_text == "é"
    assert result.metadata.original_codepoints == 2
    assert result.metadata.processed_codepoints == 1
    assert result.metadata.original_utf8_bytes == 3
    assert result.metadata.processed_utf8_bytes == 2
    assert result.metadata.normalization_changed is True


def test_invalid_configuration_is_rejected():
    with pytest.raises(InvalidConfigurationError):
        PassTextConfig(max_codepoints=0)

    with pytest.raises(InvalidConfigurationError):
        PassTextConfig(max_utf8_bytes=-1)

    with pytest.raises(InvalidConfigurationError):
        PassTextConfig(normalization="bad")
