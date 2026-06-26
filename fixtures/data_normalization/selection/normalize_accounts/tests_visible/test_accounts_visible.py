from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from accounts import normalize_accounts


def test_normalizes_aliases_merges_duplicate_ids_and_sorts():
    assert normalize_accounts(
        [
            {
                "id": 2,
                "account": {"owner": " grace hopper "},
                "contact": {"email": " GRACE@EXAMPLE.COM "},
                "enabled": "yes",
            },
            {
                "id": 1,
                "name": "ada lovelace",
                "email_address": "Ada@Example.com",
                "enabled": "disabled",
            },
            {"id": 2, "owner": "", "email": "hopper@example.com", "enabled": "inactive"},
            {"id": 1, "owner": " ADA BYRON ", "email": "", "enabled": "enabled"},
        ]
    ) == [
        {"id": 1, "owner": "Ada Byron", "email": "ada@example.com", "enabled": True},
        {"id": 2, "owner": "Grace Hopper", "email": "hopper@example.com", "enabled": True},
    ]
