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
