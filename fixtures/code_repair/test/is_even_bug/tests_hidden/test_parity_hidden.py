from pathlib import Path
import copy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parity import reconcile_status  # noqa: E402


def test_tie_breaks_by_later_input_order_and_sorts_ids():
    events = [
        {"id": "2", "status": "open", "timestamp": "5", "source": "api"},
        {"id": "10", "status": "closed", "timestamp": 1, "source": "manual"},
        {"id": "2", "status": "done", "timestamp": 5, "source": "api"},
    ]
    original = copy.deepcopy(events)
    assert reconcile_status(events) == {"10": "closed", "2": "closed"}
    assert events == original


def test_missing_source_loses_to_import_even_with_newer_timestamp():
    assert reconcile_status(
        [
            {"id": "a", "status": "open", "timestamp": 99},
            {"id": "a", "status": "blocked", "timestamp": 1, "source": "import"},
        ]
    ) == {"a": "blocked"}


def test_winning_tombstone_omits_the_id():
    assert reconcile_status(
        [
            {"id": "a", "status": "open", "timestamp": 1, "source": "api"},
            {"id": "a", "status": "archive", "timestamp": 2, "source": "api"},
            {"id": "b", "status": "deleted", "timestamp": 1, "source": "import"},
            {"id": "b", "status": "open", "timestamp": 9},
        ]
    ) == {}
