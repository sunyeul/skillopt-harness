from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from inventory import active_skus


def test_active_skus_accepts_nested_status_tokens_and_sorts_unique_skus():
    assert active_skus(
        [
            {"product": {"sku": " b-2 "}, "status": "ENABLED"},
            {"sku": "a-1", "status": "inactive"},
            {"sku": " c-3 ", "status": True},
            {"sku": "b-2", "status": "active"},
            {"product": {"sku": " "}, "status": "active"},
        ]
    ) == ["b-2", "c-3"]
