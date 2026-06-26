from preferences import preference_flags


def test_preference_flags():
    assert preference_flags(
        [{"name": " Email ", "value": "on"}, {"name": "Sms", "value": "off"}]
    ) == {"email": True, "sms": False}
