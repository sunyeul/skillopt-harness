from events import normalize_events


def test_empty_events():
    assert normalize_events([]) == []
