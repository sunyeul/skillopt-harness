import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
allocate_capacity = importlib.import_module("bounds").allocate_capacity


def test_allocates_minimums_then_priority_rounds():
    rows = [
        {"id": "a", "min": 1, "desired": 3, "priority": 1},
        {"id": "b", "min": "0", "desired": "2", "priority": 5},
        {"id": "c", "min": 1, "desired": 2, "priority": 1},
    ]
    assert allocate_capacity(rows, "5") == {"a": 2, "b": 2, "c": 1}
    assert rows[0]["desired"] == 3
