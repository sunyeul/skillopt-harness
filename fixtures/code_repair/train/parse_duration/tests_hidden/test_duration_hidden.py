import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_duration = importlib.import_module("duration").parse_duration


def test_parse_duration_accepts_unit_aliases_and_zero_boundary():
    assert parse_duration("2 hr 0 seconds") == 7200


def test_parse_duration_rejects_empty_text():
    with pytest.raises(ValueError):
        parse_duration("")


def test_parse_duration_rejects_duplicate_units():
    with pytest.raises(ValueError):
        parse_duration("1h 2hour")


def test_parse_duration_rejects_negative_values():
    with pytest.raises(ValueError):
        parse_duration("-5m")


def test_parse_duration_rejects_malformed_tokens():
    with pytest.raises(ValueError):
        parse_duration("1.5h")


def test_parse_duration_rejects_unknown_units():
    with pytest.raises(ValueError):
        parse_duration("5x")
