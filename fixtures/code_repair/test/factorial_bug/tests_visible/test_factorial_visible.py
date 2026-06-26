from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from factorial import factorial  # noqa: E402


def test_factorial_accepts_ints_and_integer_strings():
    assert factorial(6) == 720
    assert factorial("4") == 24


def test_factorial_rejects_bool_and_non_integer_values():
    with pytest.raises(ValueError):
        factorial(False)
    with pytest.raises(ValueError):
        factorial(3.5)
    with pytest.raises(ValueError):
        factorial("3.5")
