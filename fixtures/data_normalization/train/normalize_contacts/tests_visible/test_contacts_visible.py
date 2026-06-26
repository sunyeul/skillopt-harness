from contacts import normalize_contacts


def test_normalizes_and_sorts_contacts():
    assert normalize_contacts(
        [
            {"id": 2, "name": " grace hopper ", "email": " GRACE@EXAMPLE.COM "},
            {"id": 1, "name": "ada lovelace", "email": "Ada@Example.com", "active": False},
        ]
    ) == [
        {"id": 1, "name": "Ada Lovelace", "email": "ada@example.com", "active": False},
        {"id": 2, "name": "Grace Hopper", "email": "grace@example.com", "active": True},
    ]
