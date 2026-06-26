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
