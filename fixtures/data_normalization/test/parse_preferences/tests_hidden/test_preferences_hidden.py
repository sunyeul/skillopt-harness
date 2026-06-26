import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from preferences import preference_flags


def test_blank_names_false_tokens_and_duplicate_overrides_are_handled():
    assert preference_flags(
        [
            {"name": " Dark Mode ", "value": "on"},
            {"preference": "dark mode", "value": "0"},
            {"key": " ", "value": "yes"},
            {"value": "yes"},
            {"setting": "Location Sharing", "value": "enabled"},
            {"name": "location sharing", "value": None},
            {"preference": "Email", "value": 1},
        ]
    ) == {"dark mode": False, "location sharing": False, "email": True}
