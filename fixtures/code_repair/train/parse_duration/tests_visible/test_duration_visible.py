from duration import parse_duration


def test_hours_and_minutes():
    assert parse_duration("2h 15m") == 8100
