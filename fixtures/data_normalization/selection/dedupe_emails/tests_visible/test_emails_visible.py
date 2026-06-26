from emails import unique_emails


def test_unique_emails():
    assert unique_emails([" A@EXAMPLE.COM ", "b@example.com", "a@example.com", " "]) == [
        "a@example.com",
        "b@example.com",
    ]
