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


def test_order_revisions_are_selected_before_status_and_totals():
    assert totals_by_customer(
        [
            {"order_id": "o1", "customer_id": "c1", "amount": 10, "updated_at": 1},
            {"order_id": "o1", "customer_id": "c1", "amount": 20, "updated_at": 3, "status": "void"},
            {"order_id": "o2", "customer_id": "c2", "amount": "4", "updated_at": 5},
            {"order_id": "o2", "customer_id": "c2", "amount": "6", "updated_at": 5},
            {"customer_id": "c1", "amount": "1.5"},
        ]
    ) == {"c2": 6, "c1": 1.5}
