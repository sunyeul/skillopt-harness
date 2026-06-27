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


def test_updated_at_controls_duplicate_title_and_kind_fields():
    assert normalize_events(
        [
            {"id": "x", "title": " older title ", "kind": "talk", "updated_at": 10, "public": "no"},
            {"id": "x", "title": " newer title ", "kind": "", "updated_at": 20},
            {"id": "x", "title": "", "kind": " WORKSHOP ", "updated_at": 20, "public": True},
        ]
    ) == [
        {"id": "x", "title": "Newer Title", "kind": "workshop", "public": True},
    ]


def test_latest_tombstone_omits_event():
    assert normalize_events(
        [
            {"id": "gone", "title": "Old", "kind": "talk", "updated_at": 10, "public": True},
            {"id": "gone", "status": "deleted", "updated_at": 20},
            {"id": "keep", "title": "Still Here", "kind": "demo", "updated_at": 1},
        ]
    ) == [
        {"id": "keep", "title": "Still Here", "kind": "demo", "public": False},
    ]


def test_integer_one_public_token_is_public():
    assert normalize_events(
        [
            {"id": "n", "title": "numeric", "kind": "flag", "public": 1},
        ]
    ) == [
        {"id": "n", "title": "Numeric", "kind": "flag", "public": True},
    ]


def test_malformed_event_rows_are_skipped():
    assert normalize_events(
        [
            None,
            "not-an-event-row",
            {"id": "v", "title": "valid", "kind": "demo"},
        ]
    ) == [
        {"id": "v", "title": "Valid", "kind": "demo", "public": False},
    ]
