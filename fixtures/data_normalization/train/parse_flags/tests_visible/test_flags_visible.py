from flags import normalize_flags


def test_normalizes_string_flags():
    assert normalize_flags(
        [
            {"key": " Enabled ", "value": "yes"},
            {"key": "Archived", "value": "0"},
        ]
    ) == {"enabled": True, "archived": False}
