import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from events import normalize_events


def test_normalize_events_uses_aliases_merges_duplicates_and_sorts():
    assert normalize_events(
        [
            {
                "event_id": "evt-2",
                "metadata": {
                    "name": " city forum ",
                    "type": " TALK ",
                    "public": "yes",
                },
                "extra": "ignored",
            },
            {
                "id": "evt-1",
                "title": " night market ",
                "kind": " FESTIVAL ",
                "public": "private",
            },
            {
                "id": "evt-2",
                "title": " ",
                "metadata": {"type": " Workshop "},
                "public": False,
            },
        ]
    ) == [
        {"id": "evt-1", "title": "Night Market", "kind": "festival", "public": False},
        {"id": "evt-2", "title": "City Forum", "kind": "workshop", "public": True},
    ]


def test_updated_at_and_latest_tombstones_are_part_of_contract():
    assert normalize_events(
        [
            {"id": "keep", "title": "old", "kind": "talk", "updated_at": 1},
            {"id": "keep", "title": "new", "kind": "", "updated_at": 5, "public": "yes"},
            {"id": "keep", "title": "", "kind": " Workshop ", "updated_at": 5},
            {"id": "gone", "title": "old", "kind": "demo", "updated_at": 1},
            {"id": "gone", "status": "deleted", "updated_at": 9},
        ]
    ) == [
        {"id": "keep", "title": "New", "kind": "workshop", "public": True},
    ]
