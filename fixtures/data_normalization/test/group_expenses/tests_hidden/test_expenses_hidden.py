from expenses import totals_by_project


def test_missing_amount_counts_as_zero():
    assert totals_by_project([{"project_id": "p1"}, {"project_id": "p1", "amount": 2}]) == {
        "p1": 2
    }
