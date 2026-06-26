import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
add_numbers = importlib.import_module("calculator").add_numbers


def test_add_numbers_handles_negative_numeric_strings_and_zero():
    assert add_numbers("-2", 0) == -2


def test_add_numbers_rejects_booleans():
    with pytest.raises(TypeError):
        add_numbers(True, 1)

    with pytest.raises(TypeError):
        add_numbers(1, False)


def test_add_numbers_rejects_nonnumeric_strings():
    with pytest.raises(TypeError):
        add_numbers("two", 5)


def test_add_numbers_does_not_mutate_string_inputs():
    left = "-2"
    right = "5"

    assert add_numbers(left, right) == 3
    assert left == "-2"
    assert right == "5"
