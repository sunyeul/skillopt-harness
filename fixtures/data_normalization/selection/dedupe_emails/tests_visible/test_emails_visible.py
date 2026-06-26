from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from emails import unique_emails


def test_unique_emails_accepts_aliases_and_keeps_first_seen_order():
    assert unique_emails(
        [
            {"mail": " A@EXAMPLE.COM "},
            {"contact": {"email": "b@example.com"}},
            "a@example.com",
            {"email": "not-an-email"},
            " ",
        ]
    ) == [
        "a@example.com",
        "b@example.com",
    ]
