from preferences import preference_flags


def test_missing_values_are_false():
    assert preference_flags([{"name": "Push"}, {"name": "Phone", "value": None}]) == {
        "push": False,
        "phone": False,
    }
