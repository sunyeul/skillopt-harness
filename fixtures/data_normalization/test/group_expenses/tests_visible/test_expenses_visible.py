import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expenses import totals_by_project


def test_totals_by_project_accepts_aliases_amount_strings_and_order():
    result = totals_by_project(
        [
            {"project": " orbit ", "amount": "12.50", "status": "approved"},
            {"project_id": "beacon", "amount": "", "status": " approved "},
            {"project": {"id": "orbit"}, "amount": "7.5", "status": "void"},
            {"projectId": "beacon", "amount": 3},
            {"project_id": "comet", "amount": "99", "status": "rejected"},
        ]
    )

    assert result == {"orbit": 12.5, "beacon": 3}
    assert list(result) == ["orbit", "beacon"]


def test_expense_revisions_are_selected_before_status_and_totals():
    result = totals_by_project(
        [
            {"expense_id": "e-1", "project_id": "atlas", "amount": "9", "updated_at": 1},
            {"expense_id": "e-1", "project_id": "atlas", "amount": "13", "updated_at": 5},
            {"expense_id": "e-2", "project": {"id": "nova"}, "amount": "2", "updated_at": 3},
            {"expense_id": "e-2", "project": {"id": "nova"}, "amount": "4.5", "updated_at": 3},
            {"project_id": "atlas", "amount": 1},
        ]
    )

    assert list(result.items()) == [("atlas", 14), ("nova", 4.5)]
