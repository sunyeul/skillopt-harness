import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
clamp = importlib.import_module("bounds").clamp


def test_reversed_bounds_numeric_strings_and_invalid_values():
    assert clamp("5", "10", "0") == 5
    assert clamp("-2", "10", "0") == 0

    with pytest.raises(TypeError):
        clamp("five", 0, 10)


def test_int_inputs_preserve_int_result_at_boundaries():
    low_result = clamp(-4, 0, 10)
    high_result = clamp(12, 0, 10)

    assert low_result == 0
    assert high_result == 10
    assert type(low_result) is int
    assert type(high_result) is int


def test_nonnumeric_bounds_raise_type_error():
    with pytest.raises(TypeError):
        clamp(5, "low", 10)

    with pytest.raises(TypeError):
        clamp(5, 0, "high")
