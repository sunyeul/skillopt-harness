from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from timesheets import hours_by_employee


def test_hours_by_employee_accepts_aliases_strings_and_keeps_order():
    result = hours_by_employee(
        [
            {"employee": {"id": "e2"}, "hours": "1.5"},
            {"employee_id": " e1 ", "hours": ""},
            {"employee": "e2", "hours": 2, "status": "VOID"},
            {"employee": "e2", "hours": "2.25"},
        ]
    )
    assert list(result.items()) == [("e2", 3.75), ("e1", 0)]
