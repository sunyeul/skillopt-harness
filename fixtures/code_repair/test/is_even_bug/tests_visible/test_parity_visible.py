from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parity import reconcile_status  # noqa: E402


def test_merges_by_source_priority_then_timestamp():
    assert reconcile_status(
        [
            {"id": "b", "status": "open", "timestamp": 10, "source": "api"},
            {"id": "a", "status": "resolved", "timestamp": 1, "source": "import"},
            {"id": "b", "status": "hold", "timestamp": 5, "source": "manual"},
            {"id": "a", "status": "pending", "timestamp": 20, "source": "api"},
        ]
    ) == {"a": "pending", "b": "blocked"}


def test_skips_blank_ids_and_unknown_statuses():
    assert reconcile_status(
        [
            {"id": "  ", "status": "open"},
            {"item_id": "x", "status": "unknown", "timestamp": 5},
            {"item_id": "x", "status": " waiting ", "timestamp": 4},
        ]
    ) == {"x": "pending"}
