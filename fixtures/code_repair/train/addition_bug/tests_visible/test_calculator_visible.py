import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
add_numbers = importlib.import_module("calculator").add_numbers


def test_add_numbers_coerces_numeric_strings_without_mutating_inputs():
    left = "2.5"
    right = "3"

    assert add_numbers(left, right) == 5.5
    assert left == "2.5"
    assert right == "3"
