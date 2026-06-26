from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parity import is_even  # noqa: E402


def test_even_handles_zero_negative_and_signed_string():
    assert is_even(0) is True
    assert is_even(-3) is False
    assert is_even(" +42 ") is True


def test_even_rejects_bool_and_non_integer_string():
    with pytest.raises(TypeError):
        is_even(True)
    with pytest.raises(TypeError):
        is_even("4.2")
