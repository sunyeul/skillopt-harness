from palindrome import is_palindrome


def test_non_palindrome():
    assert is_palindrome("agent") is False
