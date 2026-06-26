import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
top_k_frequent = importlib.import_module("frequency").top_k_frequent


def test_normalizes_strings_skips_blanks_and_preserves_first_seen_ties():
    values = [" B ", "a", "b", "A", "", 3, 3, "3"]

    assert top_k_frequent(values, 4) == ["b", "a", 3, "3"]
    assert values == [" B ", "a", "b", "A", "", 3, 3, "3"]


def test_k_larger_than_unique_count_and_nonpositive_k():
    assert top_k_frequent(["x", " y ", "X"], 5) == ["x", "y"]
    assert top_k_frequent(["x", "x"], 0) == []
    assert top_k_frequent(["x", "x"], -1) == []


def test_dict_labels_contribute_weighted_counts():
    assert top_k_frequent(
        [
            {"label": "alpha", "weight": 2},
            " beta ",
            {"label": "beta", "weight": "2.5"},
            {"label": "gamma", "weight": "bad"},
            {"label": " ", "weight": 100},
        ],
        3,
    ) == ["beta", "alpha", "gamma"]


def test_nonpositive_weight_rows_are_ignored_before_first_seen_order():
    assert top_k_frequent(
        [
            {"label": "early", "weight": 0},
            {"label": "late", "weight": 1},
            {"label": "early", "weight": 1},
        ],
        2,
    ) == ["late", "early"]
