from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from products import published_skus


def test_missing_blank_and_unpublished_products_are_skipped():
    assert published_skus(
        [
            {"sku": "x-1"},
            {"sku": " ", "status": "published"},
            {"product": {}, "status": "live"},
            {"product": None, "status": True},
            {"sku": None, "status": "1"},
            {"sku": "a-1", "status": "PUBLISHED"},
        ]
    ) == ["a-1"]


def test_string_one_token_and_duplicate_nested_skus_collapse_before_sorting():
    assert published_skus(
        [
            {"sku": " z-9 ", "status": "1"},
            {"product": {"sku": "m-3"}, "status": "live"},
            {"sku": "m-3", "status": "published"},
            {"sku": "a-1", "status": ""},
            {"sku": "b-2", "status": False},
        ]
    ) == ["m-3", "z-9"]


def test_duplicate_skus_use_source_priority_before_status():
    assert published_skus(
        [
            {"sku": "a-1", "status": "published", "source": "feed", "updated_at": 10},
            {"sku": "A-1", "status": "draft", "source": "catalog", "updated_at": 1},
            {"product": {"sku": "b-2"}, "status": "draft", "source": "manual", "updated_at": 2},
            {"sku": "b-2", "status": "live", "source": "manual", "updated_at": 3},
            {"sku": "c-3", "status": True},
        ]
    ) == ["b-2", "c-3"]
