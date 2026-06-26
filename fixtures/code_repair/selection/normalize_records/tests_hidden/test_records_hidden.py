from records import normalize_records


def test_missing_name_and_false_active_are_preserved():
    assert normalize_records(
        [
            {"id": 3, "active": False},
            {"id": 2, "name": "  alan TURING  ", "active": False},
        ]
    ) == [
        {"id": 2, "name": "Alan Turing", "active": False},
        {"id": 3, "name": "", "active": False},
    ]
