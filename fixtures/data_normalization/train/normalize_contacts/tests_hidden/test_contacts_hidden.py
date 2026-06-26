from contacts import normalize_contacts


def test_empty_contacts():
    assert normalize_contacts([]) == []


def test_preserves_true_active():
    assert normalize_contacts(
        [{"id": 4, "name": "  alan turing", "email": "ALAN@EXAMPLE.COM", "active": True}]
    ) == [
        {"id": 4, "name": "Alan Turing", "email": "alan@example.com", "active": True}
    ]
