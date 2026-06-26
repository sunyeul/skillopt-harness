import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from categories import unique_categories


def test_unique_categories_splits_lists_and_keeps_first_seen_order():
    assert unique_categories(
        [
            " Support | Sales ",
            {"category": "support"},
            {"label": " Finance, sales "},
            "",
        ]
    ) == ["support", "sales", "finance"]
