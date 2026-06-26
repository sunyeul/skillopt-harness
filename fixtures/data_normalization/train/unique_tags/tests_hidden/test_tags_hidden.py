from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tags import unique_tags


def test_blank_none_and_non_string_values_are_skipped():
    assert unique_tags(
        [
            "",
            " ",
            "\t",
            None,
            12,
            {"tag": None},
            {"label": ["not", "a", "tag"]},
            {"name": "missing alias"},
        ]
    ) == []


def test_keeps_first_seen_order_after_case_whitespace_and_comma_normalization():
    assert unique_tags(
        [
            {"label": " Zed Tag "},
            "alpha, beta",
            {"tag": "zed   tag"},
            " ALPHA ",
            {"label": "gamma,beta"},
        ]
    ) == ["zed tag", "alpha", "beta", "gamma"]
