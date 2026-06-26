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
