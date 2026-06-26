import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
allocate_capacity = importlib.import_module("bounds").allocate_capacity


def test_tie_breaks_by_input_order_and_stops_at_desired():
    assert allocate_capacity(
        [
            {"id": "x", "min": 0, "desired": 1, "priority": 1},
            {"id": "y", "min": 0, "desired": 3, "priority": 1},
        ],
        3,
    ) == {"x": 1, "y": 2}


def test_rejects_insufficient_capacity_duplicates_and_bad_values():
    with pytest.raises(ValueError):
        allocate_capacity([{"id": "a", "min": 2, "desired": 3}], 1)
    with pytest.raises(ValueError):
        allocate_capacity([{"id": "a", "min": 0, "desired": 1}, {"id": "a", "min": 0, "desired": 1}], 1)
    with pytest.raises(ValueError):
        allocate_capacity([{"id": "a", "min": True, "desired": 1}], 1)
