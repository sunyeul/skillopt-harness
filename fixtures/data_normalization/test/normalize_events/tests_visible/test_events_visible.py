from events import normalize_events


def test_normalizes_events():
    assert normalize_events(
        [
            {"id": 5, "title": " launch day ", "kind": " WEBINAR "},
            {"id": 2, "title": "team sync", "kind": "Meeting", "public": True},
        ]
    ) == [
        {"id": 2, "title": "Team Sync", "kind": "meeting", "public": True},
        {"id": 5, "title": "Launch Day", "kind": "webinar", "public": False},
    ]
