import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from categories import category_paths


def test_tombstones_remove_descendants_and_block_readd_until_revived():
    assert category_paths(
        [
            "ops > runbooks",
            "ops > runbooks > deploy",
            {"path": "ops > runbooks", "deleted": True},
            "ops > runbooks > ignored",
            {"path": "ops > runbooks", "revive": True},
            "ops > runbooks > restore",
        ]
    ) == ["ops", "ops > runbooks", "ops > runbooks > restore"]


def test_aliases_apply_to_each_segment_case_insensitively_and_skip_bad_rows():
    assert category_paths(
        [
            {"name": "Data / ML", "aliases": {"ml": "Machine Learning", "data": "Analytics"}},
            {"label": None},
            {},
            "analytics / BI",
        ]
    ) == ["analytics", "analytics > machine learning", "analytics > bi"]


def test_reviving_descendant_path_unblocks_tombstoned_ancestors():
    assert category_paths(
        [
            "docs > api > v1",
            {"path": "docs > api", "deleted": True},
            {"path": "docs > api > v2", "revive": True},
        ]
    ) == ["docs", "docs > api", "docs > api > v2"]
