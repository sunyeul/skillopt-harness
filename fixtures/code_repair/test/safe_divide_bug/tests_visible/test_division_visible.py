from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from division import safe_divide  # noqa: E402


def test_divide_coerces_numeric_strings_and_preserves_float():
    assert safe_divide("7.5", "2.5") == 3.0
    assert safe_divide(5, 2) == 2.5


def test_divide_returns_none_for_zero_invalid_and_boolean_input():
    assert safe_divide("10", "0") is None
    assert safe_divide("ten", 2) is None
    assert safe_divide(True, 2) is None
