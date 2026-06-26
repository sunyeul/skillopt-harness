from orders import totals_by_customer


def test_missing_amount_counts_as_zero():
    assert totals_by_customer(
        [{"customer_id": "c1"}, {"customer_id": "c1", "amount": 5}]
    ) == {"c1": 5}


def test_empty_orders():
    assert totals_by_customer([]) == {}
