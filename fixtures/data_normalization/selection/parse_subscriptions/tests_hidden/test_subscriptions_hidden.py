from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from subscriptions import subscription_flags


def test_nested_plan_string_one_and_none_values():
    assert subscription_flags(
        [
            {"subscription": {"plan": "Trial"}, "enabled": "1"},
            {"name": "Enterprise", "enabled": None},
            {"plan": "trial", "enabled": "disabled"},
            {"subscription": {"plan": ""}, "enabled": "enabled"},
            {"name": "Audit", "enabled": "YES"},
        ]
    ) == {"trial": False, "enterprise": False, "audit": True}


def test_duplicate_plans_use_source_priority_timestamp_and_later_tie_break():
    assert subscription_flags(
        [
            {"plan": "Pro", "enabled": "yes", "source": "import", "updated_at": 99},
            {"plan": "pro", "enabled": "disabled", "source": "billing", "updated_at": 1},
            {"name": "Team", "enabled": "no", "source": "crm", "updated_at": 5},
            {"name": "team", "enabled": "yes", "source": "crm", "updated_at": 5},
        ]
    ) == {"pro": False, "team": True}


def test_source_priority_still_wins_when_lower_priority_is_newer():
    assert subscription_flags(
        [
            {"plan": "Audit", "enabled": "yes", "source": "import", "updated_at": 100},
            {"name": "audit", "enabled": None, "source": "billing", "updated_at": 1},
            {"subscription": {"plan": "Ops"}, "enabled": "disabled", "source": "crm", "updated_at": 8},
            {"plan": "ops", "enabled": "enabled", "source": "crm", "updated_at": 8},
        ]
    ) == {"audit": False, "ops": True}
