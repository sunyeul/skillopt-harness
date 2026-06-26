from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from division import safe_divide  # noqa: E402


def test_divide_handles_signed_and_whitespace_numeric_strings():
    assert safe_divide(" -3 ", "2") == -1.5
    assert safe_divide("6", " 4 ") == 1.5


def test_divide_returns_none_for_bad_denominator_and_boolean_values():
    assert safe_divide(1, 0) is None
    assert safe_divide(9, "bad") is None
    assert safe_divide(1, True) is None
    assert safe_divide(1, False) is None
    assert safe_divide(False, 1) is None
