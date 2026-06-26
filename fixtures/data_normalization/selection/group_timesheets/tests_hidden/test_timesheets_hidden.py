from timesheets import hours_by_employee


def test_missing_hours_are_zero():
    assert hours_by_employee([{"employee_id": "e1"}, {"employee_id": "e1", "hours": 4}]) == {
        "e1": 4
    }
