from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tags import unique_tags


def test_unique_tags_accepts_dicts_splits_commas_and_preserves_order():
    assert unique_tags(
        [
            " Bug, feature ",
            {"tag": "bug"},
            {"label": " Customer   Success "},
            "",
            {"tag": "Feature"},
            {"label": "ops,  bug"},
        ]
    ) == [
        "bug",
        "feature",
        "customer success",
        "ops",
    ]
