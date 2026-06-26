from orders import totals_by_customer


def test_totals_non_cancelled_orders():
    assert totals_by_customer(
        [
            {"customer_id": "c2", "amount": 4},
            {"customer_id": "c1", "amount": 10},
            {"customer_id": "c2", "amount": 6},
            {"customer_id": "c1", "amount": 99, "status": "cancelled"},
        ]
    ) == {"c2": 10, "c1": 10}
