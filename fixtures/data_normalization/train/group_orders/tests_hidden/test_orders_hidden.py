from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orders import totals_by_customer


def test_missing_blank_amounts_and_malformed_customers_are_handled():
    result = totals_by_customer(
        [
            {"customer_id": " c1 "},
            {"customer": {"id": "c1"}, "amount": " 2 "},
            {"customer": {"id": " "}, "amount": 100},
            {"customer": {}, "amount": 100},
            {"amount": 100},
            {"customer": "c2", "amount": None},
        ]
    )

    assert list(result.items()) == [("c1", 2), ("c2", 0)]


def test_cancelled_and_void_orders_do_not_create_or_update_customers():
    result = totals_by_customer(
        [
            {"customer_id": "c1", "amount": "1.25"},
            {"customer_id": "c2", "amount": 50, "status": "cancelled"},
            {"customer": {"id": "c3"}, "amount": 30, "status": " VOID "},
            {"customer": "c1", "amount": 2.75, "status": "complete"},
            {"customer_id": "c2", "amount": 5},
        ]
    )

    assert list(result.items()) == [("c1", 4.0), ("c2", 5)]
