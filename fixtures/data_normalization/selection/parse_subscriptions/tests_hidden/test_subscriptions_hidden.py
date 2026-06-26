from subscriptions import subscription_flags


def test_missing_and_none_values_are_false():
    assert subscription_flags(
        [{"plan": "Trial"}, {"plan": "Enterprise", "enabled": None}]
    ) == {"trial": False, "enterprise": False}
