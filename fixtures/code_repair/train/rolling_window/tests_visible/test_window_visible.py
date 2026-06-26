import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
rolling_totals = importlib.import_module("window").rolling_totals


def test_rolling_summaries_for_numbers_and_numeric_strings():
    assert rolling_totals([1, "2", 3, 4], 3) == [
        {"count": 1, "total": 1, "average": 1},
        {"count": 2, "total": 3, "average": 1.5},
        {"count": 3, "total": 6, "average": 2},
        {"count": 3, "total": 9, "average": 3},
    ]


def test_dict_readings_and_skipped_invalid_values():
    assert rolling_totals([{"value": "5"}, {"value": ""}, {"value": 7}, None], 2) == [
        {"count": 1, "total": 5, "average": 5},
        {"count": 2, "total": 12, "average": 6},
    ]
