from records import normalize_records


def test_normalizes_and_sorts_records():
    assert normalize_records(
        [
            {"id": 2, "name": " grace hopper ", "active": True},
            {"id": 1, "name": "ada lovelace"},
        ]
    ) == [
        {"id": 1, "name": "Ada Lovelace", "active": False},
        {"id": 2, "name": "Grace Hopper", "active": True},
    ]
