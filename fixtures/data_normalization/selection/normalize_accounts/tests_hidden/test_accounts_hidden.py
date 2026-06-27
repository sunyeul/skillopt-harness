from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from accounts import normalize_accounts


def test_outputs_exact_schema_with_defaults_and_nested_email():
    assert normalize_accounts(
        [
            {
                "id": 4,
                "account": {"owner": "  alan turing"},
                "contact": {"email": "ALAN@EXAMPLE.COM"},
                "enabled": True,
            },
            {"id": 5, "name": "", "email_address": "  "},
        ]
    ) == [
        {"id": 4, "owner": "Alan Turing", "email": "alan@example.com", "enabled": True},
        {"id": 5, "owner": "", "email": "", "enabled": False},
    ]


def test_duplicate_ids_keep_enabled_state_and_later_nonblank_fields():
    assert normalize_accounts(
        [
            {"id": 3, "owner": "first owner", "email": "first@example.com", "enabled": "no"},
            {"id": 3, "owner": " final owner ", "email": "", "enabled": "unknown"},
            {"id": 3, "owner": "", "email_address": "FINAL@EXAMPLE.COM", "enabled": "1"},
            {"id": 2, "owner": "earlier sort", "email": "two@example.com", "enabled": "false"},
        ]
    ) == [
        {"id": 2, "owner": "Earlier Sort", "email": "two@example.com", "enabled": False},
        {"id": 3, "owner": "Final Owner", "email": "final@example.com", "enabled": True},
    ]


def test_duplicate_ids_use_updated_at_for_owner_and_email_fields():
    assert normalize_accounts(
        [
            {"id": 7, "owner": "old owner", "email": "old@example.com", "updated_at": 10, "enabled": "no"},
            {"id": 7, "owner": "new owner", "email": "", "updated_at": 20, "enabled": "disabled"},
            {"id": 7, "owner": "", "email": "NEW@EXAMPLE.COM", "updated_at": 20, "enabled": "enabled"},
            {"id": 8, "name": " no timestamp ", "email": "nt@example.com"},
        ]
    ) == [
        {"id": 7, "owner": "New Owner", "email": "new@example.com", "enabled": True},
        {"id": 8, "owner": "No Timestamp", "email": "nt@example.com", "enabled": False},
    ]


def test_rows_without_account_ids_are_ignored_before_sorting():
    assert normalize_accounts(
        [
            {"owner": "ghost", "email": "ghost@example.com", "enabled": True},
            {"id": 9, "owner": " real owner ", "email": "REAL@EXAMPLE.COM"},
        ]
    ) == [
        {"id": 9, "owner": "Real Owner", "email": "real@example.com", "enabled": False},
    ]
