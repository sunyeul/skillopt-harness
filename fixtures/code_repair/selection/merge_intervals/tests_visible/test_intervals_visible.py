import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
merge_intervals = importlib.import_module("intervals").merge_intervals


def test_reversed_touching_and_nested_intervals_merge_without_mutation():
    intervals = [[5, 3], [1, 2], [2, 4], [10, 12], [11, 11]]

    assert merge_intervals(intervals) == [[1, 5], [10, 12]]
    assert intervals == [[5, 3], [1, 2], [2, 4], [10, 12], [11, 11]]
