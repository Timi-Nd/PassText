import json
from pathlib import Path

from passtext import InvalidUnicodeError, PassTextConfig, process_password

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "rust_portability_vectors.json"


def load_fixtures():
    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_portability_fixture_file_is_valid_json_and_consistent():
    fixtures = load_fixtures()
    assert len(fixtures) >= 3
    assert fixtures[0]["name"] == "ascii_basic"

    result = process_password(fixtures[0]["input"], config=PassTextConfig(**fixtures[0]["config"]))
    assert result.metadata.original_codepoints == fixtures[0]["expected"]["original_codepoints"]
    assert result.metadata.processed_utf8_bytes == fixtures[0]["expected"]["processed_utf8_bytes"]

    nfc_result = process_password(
        fixtures[1]["input"],
        config=PassTextConfig(**fixtures[1]["config"]),
    )
    assert nfc_result.metadata.normalization_changed is True
    assert nfc_result.processed_text == "é"

    try:
        process_password(fixtures[2]["input"], config=PassTextConfig(**fixtures[2]["config"]))
    except InvalidUnicodeError:
        return
    raise AssertionError("expected InvalidUnicodeError from surrogate fixture")
