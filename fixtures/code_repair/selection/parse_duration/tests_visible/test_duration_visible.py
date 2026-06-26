import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parse_duration = importlib.import_module("duration").parse_duration


def test_accepts_aliases_commas_punctuation_and_case_insensitive_units():
    assert parse_duration("1 hr, 2 minutes, 3 Sec.") == 3723
