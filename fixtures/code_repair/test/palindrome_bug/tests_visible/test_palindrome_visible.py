from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from palindrome import is_palindrome  # noqa: E402


def test_palindrome_ignores_case_spaces_and_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama!") is True


def test_palindrome_detects_non_palindrome_and_rejects_non_strings():
    assert is_palindrome("OpenAI") is False
    with pytest.raises(TypeError):
        is_palindrome(12321)
