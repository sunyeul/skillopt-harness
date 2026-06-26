from accounts import normalize_accounts


def test_normalizes_accounts():
    assert normalize_accounts(
        [
            {"id": 3, "owner": "  jane doe", "email": "JANE@EXAMPLE.COM"},
            {"id": 1, "owner": "john smith", "email": " john@example.com ", "enabled": True},
        ]
    ) == [
        {"id": 1, "owner": "John Smith", "email": "john@example.com", "enabled": True},
        {"id": 3, "owner": "Jane Doe", "email": "jane@example.com", "enabled": False},
    ]
