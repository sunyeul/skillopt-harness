from flags import normalize_flags


def test_missing_and_blank_values_are_false():
    assert normalize_flags(
        [
            {"key": "Beta"},
            {"key": "Internal", "value": ""},
            {"key": "Public", "value": None},
        ]
    ) == {"beta": False, "internal": False, "public": False}


def test_boolean_values_are_preserved():
    assert normalize_flags(
        [{"key": "Ready", "value": True}, {"key": "Deleted", "value": False}]
    ) == {"ready": True, "deleted": False}
