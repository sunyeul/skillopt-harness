import pytest

from duration import parse_duration


def test_case_whitespace_and_invalid_tokens():
    assert parse_duration(" 2M   7s ") == 127
    with pytest.raises(ValueError):
        parse_duration("3d")
