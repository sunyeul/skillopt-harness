from expenses import totals_by_project


def test_totals_by_project():
    assert totals_by_project(
        [
            {"project_id": "p2", "amount": 3},
            {"project_id": "p1", "amount": 8},
            {"project_id": "p2", "amount": 7},
            {"project_id": "p1", "amount": 100, "status": "rejected"},
        ]
    ) == {"p2": 10, "p1": 8}
