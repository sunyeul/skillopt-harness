from subscriptions import subscription_flags


def test_subscription_flags():
    assert subscription_flags(
        [
            {"plan": " Pro ", "enabled": "enabled"},
            {"plan": "Free", "enabled": "no"},
        ]
    ) == {"pro": True, "free": False}
