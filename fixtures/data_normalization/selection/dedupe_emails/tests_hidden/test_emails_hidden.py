from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from emails import unique_emails


def test_nested_contact_and_invalid_rows_do_not_change_order():
    assert unique_emails(
        [
            {"contact": {"email": " Z@EXAMPLE.COM "}},
            {"mail": "missing-at"},
            {"email": "a@example.com"},
            {"contact": {"email": "z@example.com"}},
            {"mail": ""},
            " A@EXAMPLE.COM ",
        ]
    ) == [
        "z@example.com",
        "a@example.com",
    ]
