from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contacts import normalize_contacts


def test_normalizes_aliases_merges_duplicate_ids_and_sorts():
    assert normalize_contacts(
        [
            {"id": 2, "name": " grace hopper ", "contact": {"email": " GRACE@EXAMPLE.COM "}, "active": "yes"},
            {"id": 1, "name": "ada lovelace", "email_address": "Ada@Example.com", "active": "disabled"},
            {"id": 2, "name": "", "email": "hopper@example.com", "active": "inactive"},
            {"id": 1, "name": " ADA BYRON ", "email": "", "active": "enabled"},
        ]
    ) == [
        {"id": 1, "name": "Ada Byron", "email": "ada@example.com", "active": True},
        {"id": 2, "name": "Grace Hopper", "email": "hopper@example.com", "active": False},
    ]
