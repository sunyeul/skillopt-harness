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
