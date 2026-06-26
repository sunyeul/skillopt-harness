import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from events import normalize_events


def test_exact_schema_duplicate_resolution_and_malformed_rows():
    result = normalize_events(
        [
            {
                "metadata": {
                    "id": "b",
                    "title": " beta launch ",
                    "kind": " DEMO ",
                },
                "public": "no",
                "extra": "drop",
            },
            {
                "id": "a",
                "title": " alpha social ",
                "kind": " Meetup ",
                "public": "public",
                "location": "roof",
            },
            {"event_id": "b", "title": " beta revised ", "kind": " ", "public": True},
            {"id": "a", "metadata": {"title": " ", "type": " PANEL "}, "public": "1"},
            {
                "metadata": {
                    "id": "c",
                    "name": " civic clinic ",
                    "type": " TRAINING ",
                    "visibility": "public",
                }
            },
            {"id": " ", "title": "skip me", "kind": "talk", "public": True},
            {"title": "missing id", "kind": "talk", "public": "public"},
        ]
    )

    assert result == [
        {"id": "a", "title": "Alpha Social", "kind": "panel", "public": True},
        {"id": "b", "title": "Beta Revised", "kind": "demo", "public": True},
        {"id": "c", "title": "Civic Clinic", "kind": "training", "public": True},
    ]
    assert [list(event) for event in result] == [
        ["id", "title", "kind", "public"],
        ["id", "title", "kind", "public"],
        ["id", "title", "kind", "public"],
    ]
