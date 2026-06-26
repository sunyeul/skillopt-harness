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
