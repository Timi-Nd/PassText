import pytest

from passtext import PassTextConfig, process_password
from passtext.indexing import (
    TextSpan,
    codepoint_index_for_utf8_offset,
    slice_text,
    utf8_offset_for_codepoint,
)


def test_metadata_as_dict_excludes_secret_contents():
    result = process_password("éA🙂", config=PassTextConfig())
    payload = result.metadata.as_dict()

    assert payload["original_codepoints"] == 3
    assert payload["processed_utf8_bytes"] == 7
    assert "éA🙂" not in str(payload)
    assert "🙂" not in str(payload)


def test_indexing_round_trip_for_utf8_and_codepoint_offsets():
    text = "éA🙂"

    assert utf8_offset_for_codepoint(text, 0) == 0
    assert utf8_offset_for_codepoint(text, 1) == 2
    assert utf8_offset_for_codepoint(text, 2) == 3
    assert utf8_offset_for_codepoint(text, 3) == 7

    assert codepoint_index_for_utf8_offset(text, 0) == 0
    assert codepoint_index_for_utf8_offset(text, 2) == 1
    assert codepoint_index_for_utf8_offset(text, 3) == 2
    assert codepoint_index_for_utf8_offset(text, 7) == 3

    assert slice_text(text, TextSpan(1, 3)) == "A🙂"


def test_indexing_rejects_mid_codepoint_utf8_offsets():
    with pytest.raises(ValueError, match="UTF-8 offset"):
        codepoint_index_for_utf8_offset("éA", 1)
