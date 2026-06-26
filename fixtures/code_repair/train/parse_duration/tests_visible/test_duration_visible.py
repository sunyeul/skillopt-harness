import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_duration = importlib.import_module("duration").parse_duration


def test_parse_duration_accepts_compact_spaced_and_case_insensitive_units():
    assert parse_duration("1Hour 15 min 30S") == 4530
