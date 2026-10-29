import json
from pathlib import Path

import pytest

from passtext import (
    InvalidUnicodeError,
    PassTextConfig,
    ProcessingLimitError,
    process_password,
)
from passtext.indexing import (
    TextSpan,
    codepoint_index_for_utf8_offset,
    slice_text,
    utf8_offset_for_codepoint,
)

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "rust_portability_vectors.json"


def load_fixtures():
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_process_and_error_vectors_match_the_portable_contract():
    fixtures = load_fixtures()
    error_types = {
        "InvalidUnicodeError": InvalidUnicodeError,
        "ProcessingLimitError": ProcessingLimitError,
    }

    assert fixtures["schema_version"] == 1
    assert "Unicode scalar" in fixtures["unicode_representation"]

    for vector in fixtures["cases"]:
        config = PassTextConfig(**vector["config"])
        if vector["operation"] == "process_error":
            expected_error = error_types[vector["expected_error"]]
            with pytest.raises(expected_error):
                process_password(vector["input"], config=config)
            continue

        assert vector["operation"] == "process"
        result = process_password(vector["input"], config=config)
        assert result.processed_text == vector["expected"]["processed_text"]
        metadata = result.metadata.as_dict()
        for key, expected_value in vector["expected"].items():
            if key != "processed_text":
                assert metadata[key] == expected_value, vector["name"]


def test_indexing_vectors_match_codepoint_and_utf8_boundaries():
    fixtures = load_fixtures()
    assert fixtures["indexing"]

    for vector in fixtures["indexing"]:
        text = vector["text"]
        byte_boundaries = vector["codepoint_to_utf8"]
        codepoint_boundaries = vector["utf8_to_codepoint"]

        assert len(byte_boundaries) == len(text) + 1
        assert len(codepoint_boundaries) == len(byte_boundaries)
        for codepoint_index, (byte_offset, expected_index) in enumerate(
            zip(byte_boundaries, codepoint_boundaries, strict=True)
        ):
            assert utf8_offset_for_codepoint(text, codepoint_index) == byte_offset
            assert codepoint_index_for_utf8_offset(text, byte_offset) == expected_index
            assert expected_index == codepoint_index

        for byte_offset in vector["invalid_utf8_offsets"]:
            with pytest.raises(ValueError, match="UTF-8 offset"):
                codepoint_index_for_utf8_offset(text, byte_offset)

        for span in vector["spans"]:
            assert slice_text(text, TextSpan(span["start"], span["end"])) == span["expected"]
