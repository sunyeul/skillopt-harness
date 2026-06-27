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


def test_duplicate_plans_use_source_priority_before_timestamp_and_order():
    assert subscription_flags(
        [
            {"plan": "starter", "enabled": "yes", "source": "import", "updated_at": 99},
            {"name": "Starter", "enabled": "enabled", "source": "billing", "updated_at": 1},
            {"subscription": {"plan": "enterprise"}, "enabled": "no", "source": "crm", "updated_at": 4},
            {"plan": " Enterprise ", "enabled": "enabled", "source": "crm", "updated_at": 4},
        ]
    ) == {"starter": True, "enterprise": True}
