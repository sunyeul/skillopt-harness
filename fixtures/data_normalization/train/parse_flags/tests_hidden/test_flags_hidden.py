from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flags import normalize_flags


def test_blank_keys_are_skipped_and_later_rows_override():
    assert normalize_flags(
        [
            {"name": " Beta ", "value": "yes"},
            {"key": "beta", "value": "off"},
            {"key": " ", "value": "yes"},
            {"name": "Internal", "value": None},
        ]
    ) == {"beta": False, "internal": False}


def test_unknown_missing_and_blank_values_are_false():
    assert normalize_flags(
        [
            {"key": "Ready", "value": "maybe"},
            {"name": "Deleted", "value": False},
            {"key": "Public", "value": ""},
            {"name": "Defaulted"},
        ]
    ) == {"ready": False, "deleted": False, "public": False, "defaulted": False}
