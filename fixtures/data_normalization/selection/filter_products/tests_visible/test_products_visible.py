from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from products import published_skus


def test_published_skus_accepts_nested_tokens_and_sorts_unique_skus():
    assert published_skus(
        [
            {"product": {"sku": " b-2 "}, "status": "live"},
            {"sku": "a-1", "status": "draft"},
            {"sku": " c-3 ", "status": True},
            {"sku": "b-2", "status": "published"},
            {"product": {"sku": " "}, "status": "published"},
        ]
    ) == ["b-2", "c-3"]


def test_duplicate_skus_choose_source_priority_before_timestamp_and_status():
    assert published_skus(
        [
            {"sku": "p-1", "status": "published", "source": "feed", "updated_at": 30},
            {"product": {"sku": " P-1 "}, "status": "published", "source": "catalog", "updated_at": 1},
            {"sku": "q-2", "status": "draft", "source": "manual", "updated_at": 2},
            {"sku": "Q-2", "status": "live", "source": "manual", "updated_at": 3},
        ]
    ) == ["p-1", "q-2"]
