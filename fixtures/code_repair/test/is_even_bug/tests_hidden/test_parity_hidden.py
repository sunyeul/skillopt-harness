from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parity import is_even  # noqa: E402


def test_even_negative_integer_strings_and_odd_values():
    assert is_even(" -18 ") is True
    assert is_even(-7) is False


def test_even_rejects_bool_blank_and_words():
    with pytest.raises(TypeError):
        is_even(False)
    with pytest.raises(TypeError):
        is_even("   ")
    with pytest.raises(TypeError):
        is_even("twelve")
