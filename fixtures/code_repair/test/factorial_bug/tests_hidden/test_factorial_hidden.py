from pathlib import Path
import math
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from factorial import factorial  # noqa: E402


def test_integer_strings_zero_and_invalid_values():
    assert factorial("5") == 120
    assert factorial(0) == 1
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        factorial(True)


def test_moderate_input_avoids_recursion_limits():
    assert factorial(1200) == math.factorial(1200)
