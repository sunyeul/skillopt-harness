from people import normalize_people


def test_normalizes_defaults_and_sorts_people():
    assert normalize_people(
        [
            {"id": 3, "name": " grace hopper ", "active": True},
            {"id": 1, "name": "ada lovelace"},
        ]
    ) == [
        {"id": 1, "name": "Ada Lovelace", "active": False},
        {"id": 3, "name": "Grace Hopper", "active": True},
    ]
