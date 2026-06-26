import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_duration = importlib.import_module("duration").parse_duration


def test_accepts_compact_spaced_aliases_and_terminal_punctuation():
    assert parse_duration("2HOURS, 0 min, 5seconds!") == 7205


def test_rejects_empty_text():
    with pytest.raises(ValueError):
        parse_duration("")


def test_rejects_duplicate_units():
    with pytest.raises(ValueError):
        parse_duration("1h 2 hours")


def test_rejects_negative_values():
    with pytest.raises(ValueError):
        parse_duration("-5m")


def test_rejects_malformed_tokens():
    with pytest.raises(ValueError):
        parse_duration("1.5h")


def test_rejects_unknown_units():
    with pytest.raises(ValueError):
        parse_duration("3d")
