import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expenses import totals_by_project


def test_rejected_void_blank_amounts_and_malformed_projects_are_handled():
    result = totals_by_project(
        [
            {"project_id": " p2 ", "amount": "4", "status": "approved"},
            {"project": {"id": "p1"}},
            {"projectId": "p2", "amount": "6.25", "status": " rejected "},
            {"project": "p1", "amount": "1.75", "status": "VOID"},
            {"project": {"id": "p2"}, "amount": "2.5"},
            {"project_id": " ", "amount": "99"},
            {"amount": "3"},
        ]
    )

    assert result == {"p2": 6.5, "p1": 0}
    assert list(result) == ["p2", "p1"]
