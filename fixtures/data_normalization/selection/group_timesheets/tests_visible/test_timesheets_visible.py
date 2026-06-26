from timesheets import hours_by_employee


def test_hours_by_employee():
    assert hours_by_employee(
        [
            {"employee_id": "e2", "hours": 2},
            {"employee_id": "e1", "hours": 5},
            {"employee_id": "e2", "hours": 3},
            {"employee_id": "e1", "hours": 9, "status": "rejected"},
        ]
    ) == {"e2": 5, "e1": 5}
