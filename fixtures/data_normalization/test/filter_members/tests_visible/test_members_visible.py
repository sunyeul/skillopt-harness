import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from members import active_member_ids


def test_active_member_ids_accepts_aliases_tokens_and_sorts_unique_ids():
    assert active_member_ids(
        [
            {"member_id": " z9 ", "status": "enabled"},
            {"member": {"id": "a1"}, "status": "yes"},
            {"id": "z9", "status": True},
            {"id": "b2", "status": "active"},
            {"user_id": "c3", "status": "1"},
            {"id": " ", "status": "active"},
        ]
    ) == ["a1", "b2", "c3", "z9"]
