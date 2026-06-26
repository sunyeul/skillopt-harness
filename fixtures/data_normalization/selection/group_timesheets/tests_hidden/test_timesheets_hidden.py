from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from timesheets import hours_by_employee


def test_rejected_status_is_trimmed_and_first_seen_order_is_stable():
    result = hours_by_employee(
        [
            {"employee_id": "beta", "hours": 1},
            {"employee": {"id": "alpha"}, "hours": "2"},
            {"employee": " beta ", "hours": "9", "status": " rejected "},
            {"employee": {"id": "beta"}, "hours": None},
            {"employee_id": "alpha", "hours": "3.5"},
        ]
    )
    assert list(result.items()) == [("beta", 1), ("alpha", 5.5)]


def test_row_revisions_are_selected_before_status_and_totals():
    result = hours_by_employee(
        [
            {"row_id": "r1", "employee_id": "ann", "hours": 8, "submitted_at": 1},
            {"row_id": "r1", "employee_id": "ann", "hours": 6, "submitted_at": 3, "status": "void"},
            {"row_id": "r2", "employee_id": "bob", "hours": "2.5", "submitted_at": 5},
            {"row_id": "r2", "employee_id": "bob", "hours": "3.5", "submitted_at": 5},
            {"employee_id": "ann", "hours": "1.5"},
        ]
    )
    assert list(result.items()) == [("bob", 3.5), ("ann", 1.5)]
