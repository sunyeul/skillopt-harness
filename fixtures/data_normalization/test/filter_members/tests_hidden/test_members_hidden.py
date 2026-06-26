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
