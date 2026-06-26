from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from subscriptions import subscription_flags


def test_subscription_flags_accepts_plan_aliases_tokens_and_later_override():
    assert subscription_flags(
        [
            {"name": " Pro ", "enabled": "enabled"},
            {"subscription": {"plan": "Free"}, "enabled": "no"},
            {"plan": "pro", "enabled": ""},
            {"plan": " ", "enabled": "yes"},
            {"name": "Team", "enabled": True},
        ]
    ) == {"pro": False, "free": False, "team": True}
