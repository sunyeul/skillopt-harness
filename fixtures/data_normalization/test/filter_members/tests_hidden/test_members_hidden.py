import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from members import active_member_ids


def test_aliases_duplicates_and_blank_ids_are_handled():
    assert active_member_ids(
        [
            {"member": {"id": " m2 "}, "status": "yes"},
            {"member_id": "m1", "status": "disabled"},
            {"id": "m2", "status": True},
            {"id": " ", "status": "active"},
            {"member": {"id": "m0"}, "status": "1"},
        ]
    ) == ["m0", "m2"]


def test_duplicate_members_use_source_priority_before_timestamp():
    assert active_member_ids(
        [
            {"id": "a", "status": "active", "source": "import", "updated_at": 10},
            {"member_id": "a", "status": "disabled", "source": "manual", "updated_at": 1},
            {"user_id": "b", "status": "inactive", "source": "directory", "updated_at": 5},
            {"id": "b", "status": "enabled", "source": "directory", "updated_at": 5},
            {"id": "c", "status": "yes"},
        ]
    ) == ["b", "c"]
