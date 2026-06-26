import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
rank_labels = importlib.import_module("frequency").rank_labels


def test_rank_labels_skips_blank_labels_and_uses_canonical_first_seen_order():
    labels = [" Beta ", "alpha", "ALPHA", " ", "beta", "gamma"]

    assert rank_labels(labels, 3) == ["beta", "alpha", "gamma"]
    assert labels == [" Beta ", "alpha", "ALPHA", " ", "beta", "gamma"]


def test_limit_larger_than_unique_count():
    assert rank_labels(["x", " y ", "X"], 5) == ["x", "y"]


def test_nonpositive_limits_return_empty_list():
    assert rank_labels(["x", "x"], 0) == []
    assert rank_labels(["x", "x"], -1) == []
