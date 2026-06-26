from people import normalize_people


def test_preserves_false_active_and_sorts_multiple_people():
    assert normalize_people(
        [
            {"id": 2, "name": "katherine johnson", "active": False},
            {"id": 1, "name": "  mary jackson  ", "active": True},
        ]
    ) == [
        {"id": 1, "name": "Mary Jackson", "active": True},
        {"id": 2, "name": "Katherine Johnson", "active": False},
    ]


def test_empty_input_returns_empty_list():
    assert normalize_people([]) == []
