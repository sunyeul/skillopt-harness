from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from palindrome import is_palindrome  # noqa: E402


def test_palindrome_empty_normalized_and_mixed_alphanumeric_cases():
    assert is_palindrome("... !!!") is True
    assert is_palindrome("No 'x' in Nixon") is True
    assert is_palindrome("12 3,21") is True


def test_palindrome_rejects_none_and_detects_order_mismatch():
    assert is_palindrome("palindrome? no") is False
    with pytest.raises(TypeError):
        is_palindrome(None)
