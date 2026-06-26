import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from categories import unique_categories


def test_dict_aliases_whitespace_normalization_and_malformed_rows():
    assert unique_categories(
        [
            {"name": " Data  Science, Research "},
            "research | Ops",
            {"category": "ops, Customer Success"},
            {"label": " "},
            {},
            {"category": None},
        ]
    ) == ["data science", "research", "ops", "customer success"]
