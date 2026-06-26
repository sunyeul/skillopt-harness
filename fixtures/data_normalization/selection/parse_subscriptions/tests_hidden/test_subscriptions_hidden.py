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
