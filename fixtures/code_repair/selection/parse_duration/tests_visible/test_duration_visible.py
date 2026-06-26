from duration import parse_duration


def test_hours_minutes_and_seconds():
    assert parse_duration("1h 30m 5s") == 5405
