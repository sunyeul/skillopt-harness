from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orders import totals_by_customer


def test_totals_accept_customer_aliases_numeric_strings_and_preserve_order():
    assert totals_by_customer(
        [
            {"customer": {"id": " c2 "}, "amount": "4.5"},
            {"customer_id": "c1", "amount": 10},
            {"customer": "c2", "amount": 6},
            {"customer_id": "c1", "amount": 99, "status": "cancelled"},
            {"customer": {"id": "c3"}, "amount": "", "status": "paid"},
            {"customer_id": "c3", "amount": 2, "status": "VOID"},
        ]
    ) == {"c2": 10.5, "c1": 10, "c3": 0}
