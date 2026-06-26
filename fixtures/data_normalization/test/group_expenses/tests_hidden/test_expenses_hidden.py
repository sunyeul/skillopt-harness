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


def test_expense_revisions_are_selected_before_totals():
    result = totals_by_project(
        [
            {"expense_id": "e1", "project_id": "p1", "amount": "10", "updated_at": 1},
            {"expense_id": "e1", "project_id": "p1", "amount": "15", "updated_at": 3, "status": "void"},
            {"expense_id": "e2", "project_id": "p2", "amount": "2", "updated_at": 4},
            {"expense_id": "e2", "project_id": "p2", "amount": "5", "updated_at": 4},
            {"project_id": "p1", "amount": "1.25"},
        ]
    )
    assert list(result.items()) == [("p2", 5), ("p1", 1.25)]
