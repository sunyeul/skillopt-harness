from emails import unique_emails


def test_keeps_first_seen_order():
    assert unique_emails(["z@example.com", "A@example.com", " z@example.com "]) == [
        "z@example.com",
        "a@example.com",
    ]
