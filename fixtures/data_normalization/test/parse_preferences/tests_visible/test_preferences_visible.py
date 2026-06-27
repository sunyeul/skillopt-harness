import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from preferences import preference_flags


def test_preference_flags_accepts_name_aliases_and_later_overrides():
    assert preference_flags(
        [
            {"preference": " Weekly Digest ", "value": "yes"},
            {"key": "beta access", "value": "disabled"},
            {"name": "weekly digest", "value": "off"},
            {"setting": "Sms Alerts", "value": True},
        ]
    ) == {"weekly digest": False, "beta access": False, "sms alerts": True}


def test_scope_priority_timestamp_and_locking_are_part_of_visible_contract():
    assert preference_flags(
        [
            {"name": "reports", "value": "yes", "scope": "global", "updated_at": 10},
            {"preference": " Reports ", "value": "0", "scope": "group", "updated_at": 1},
            {"key": "alerts", "value": "off", "scope": "group", "locked": True, "updated_at": 2},
            {"name": "alerts", "value": "on", "scope": "user", "updated_at": 3},
        ]
    ) == {"reports": False, "alerts": True}
