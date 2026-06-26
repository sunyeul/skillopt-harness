import pytest

from duration import parse_duration


def test_minutes_and_seconds():
    assert parse_duration("3m 5s") == 185


def test_seconds_only():
    assert parse_duration("45s") == 45


def test_invalid_unit_raises_value_error():
    with pytest.raises(ValueError):
        parse_duration("5x")
