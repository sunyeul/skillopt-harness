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


def test_duplicate_preferences_use_scope_priority_then_timestamp():
    assert preference_flags(
        [
            {"name": "email", "value": "yes", "scope": "global", "updated_at": 10},
            {"preference": " Email ", "value": "0", "scope": "group", "updated_at": 1},
            {"key": "sms", "value": "no", "scope": "user", "updated_at": 2},
            {"setting": "sms", "value": "enabled", "scope": "user", "updated_at": 3},
        ]
    ) == {"email": False, "sms": True}


def test_locked_rows_block_lower_priority_scope_only():
    assert preference_flags(
        [
            {"name": "beta", "value": "yes", "scope": "group", "locked": True, "updated_at": 1},
            {"name": "beta", "value": "no", "scope": "global", "updated_at": 99},
            {"name": "beta", "value": "no", "scope": "user", "updated_at": 2},
        ]
    ) == {"beta": False}


def test_same_scope_timestamp_ties_and_higher_scope_override_locks():
    assert preference_flags(
        [
            {"name": "exports", "value": "off", "scope": "group", "updated_at": 5},
            {"preference": "exports", "value": "on", "scope": "group", "updated_at": 5},
            {"key": "sharing", "value": "enabled", "scope": "global", "locked": True, "updated_at": 20},
            {"setting": "sharing", "value": "0", "scope": "user", "updated_at": 1},
        ]
    ) == {"exports": True, "sharing": False}
