import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
merge_intervals = importlib.import_module("intervals").merge_intervals


def test_negative_reversed_intervals_sort_merge_and_preserve_input():
    intervals = [[10, 12], [-1, -3], [-2, 5], [11, 11]]

    assert merge_intervals(intervals) == [[-3, 5], [10, 12]]
    assert intervals == [[10, 12], [-1, -3], [-2, 5], [11, 11]]


def test_malformed_intervals_raise_value_error():
    with pytest.raises(ValueError):
        merge_intervals([[1, 2], [3]])

    with pytest.raises(ValueError):
        merge_intervals([[1, 2, 3]])
