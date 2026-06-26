from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from inventory import active_skus


def test_missing_blank_and_malformed_skus_are_skipped():
    assert active_skus(
        [
            {"sku": "x-1"},
            {"sku": " ", "status": "active"},
            {"product": {}, "status": "active"},
            {"product": None, "status": "active"},
            {"sku": None, "status": "enabled"},
            {"sku": "a-1", "status": "Active"},
        ]
    ) == ["a-1"]


def test_string_one_token_and_duplicate_nested_skus_collapse_before_sorting():
    assert active_skus(
        [
            {"sku": " z-9 ", "status": "1"},
            {"product": {"sku": "m-3"}, "status": "enabled"},
            {"sku": "m-3", "status": "ACTIVE"},
            {"sku": "a-1", "status": ""},
            {"sku": "b-2", "status": False},
        ]
    ) == ["m-3", "z-9"]


def test_duplicate_skus_use_source_priority_before_status():
    assert active_skus(
        [
            {"sku": "a-1", "status": "active", "source": "feed", "updated_at": 10},
            {"sku": "A-1", "status": "inactive", "source": "catalog", "updated_at": 1},
            {"product": {"sku": "b-2"}, "status": "inactive", "source": "manual", "updated_at": 2},
            {"sku": "b-2", "status": "enabled", "source": "manual", "updated_at": 3},
            {"sku": "c-3", "status": True},
        ]
    ) == ["b-2", "c-3"]
