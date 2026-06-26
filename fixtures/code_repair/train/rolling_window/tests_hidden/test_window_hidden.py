import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
rolling_totals = importlib.import_module("window").rolling_totals


def test_boolean_and_missing_values_are_skipped_without_output():
    assert rolling_totals([True, {"value": 2.5}, {}, "3.5", False], 2) == [
        {"count": 1, "total": 2.5, "average": 2.5},
        {"count": 2, "total": 6, "average": 3},
    ]


def test_window_must_be_positive_integer():
    with pytest.raises(ValueError):
        rolling_totals([1, 2], 0)
    with pytest.raises(ValueError):
        rolling_totals([1, 2], "2")


def test_reset_rows_clear_the_current_window_before_value():
    assert rolling_totals([1, 2, {"reset": True}, 3, {"reset": True, "value": 4}, 5], 2) == [
        {"count": 1, "total": 1, "average": 1},
        {"count": 2, "total": 3, "average": 1.5},
        {"count": 1, "total": 3, "average": 3},
        {"count": 1, "total": 4, "average": 4},
        {"count": 2, "total": 9, "average": 4.5},
    ]
