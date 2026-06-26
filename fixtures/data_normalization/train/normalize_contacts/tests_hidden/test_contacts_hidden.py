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
