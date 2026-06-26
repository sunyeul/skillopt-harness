import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from categories import category_paths


def test_builds_preorder_paths_with_aliases_and_sibling_order():
    assert category_paths(
        [
            "Products > Hardware > Laptops",
            {"path": "Products/Software", "aliases": {"Products": "Catalog"}},
            " catalog > hardware > Monitors ",
        ]
    ) == [
        "products",
        "products > hardware",
        "products > hardware > laptops",
        "catalog",
        "catalog > software",
        "catalog > hardware",
        "catalog > hardware > monitors",
    ]


def test_tombstones_block_descendants_until_revived():
    assert category_paths(
        [
            "Ops > Runbooks",
            "Ops > Runbooks > Deploy",
            {"path": "Ops > Runbooks", "deleted": True},
            "Ops > Runbooks > Ignored",
            {"path": "Ops > Runbooks", "revive": True},
            "Ops > Runbooks > Restore",
        ]
    ) == ["ops", "ops > runbooks", "ops > runbooks > restore"]
