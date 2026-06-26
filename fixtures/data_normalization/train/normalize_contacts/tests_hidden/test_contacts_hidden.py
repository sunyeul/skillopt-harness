from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contacts import normalize_contacts


def test_outputs_exact_schema_with_defaults_and_nested_email():
    assert normalize_contacts(
        [
            {"id": 4, "name": "  alan turing", "contact": {"email": "ALAN@EXAMPLE.COM"}, "active": True},
            {"id": 5, "name": "", "email_address": "  "},
        ]
    ) == [
        {"id": 4, "name": "Alan Turing", "email": "alan@example.com", "active": True},
        {"id": 5, "name": "", "email": "", "active": False},
    ]


def test_duplicate_ids_keep_active_state_and_later_nonblank_fields():
    assert normalize_contacts(
        [
            {"id": 3, "name": "first name", "email": "first@example.com", "active": "no"},
            {"id": 3, "name": " final name ", "email": "", "active": "unknown"},
            {"id": 3, "name": "", "email_address": "FINAL@EXAMPLE.COM", "active": "1"},
            {"id": 2, "name": "earlier sort", "email": "two@example.com", "active": "false"},
        ]
    ) == [
        {"id": 2, "name": "Earlier Sort", "email": "two@example.com", "active": False},
        {"id": 3, "name": "Final Name", "email": "final@example.com", "active": True},
    ]


def test_duplicate_ids_use_source_priority_and_tombstone_winner():
    assert normalize_contacts(
        [
            {"id": 9, "name": "old", "email": "old@example.com", "active": "yes", "source": "import", "updated_at": 10},
            {"id": 9, "name": "manual", "email": "manual@example.com", "active": "no", "source": "manual", "updated_at": 1},
            {"id": 10, "name": "keep", "email": "keep@example.com", "source": "crm", "updated_at": 1},
            {"id": 10, "status": "deleted", "source": "manual", "updated_at": 0},
        ]
    ) == [
        {"id": 9, "name": "Manual", "email": "manual@example.com", "active": False},
    ]
