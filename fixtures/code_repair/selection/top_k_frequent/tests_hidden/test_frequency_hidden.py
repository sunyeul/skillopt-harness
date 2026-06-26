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
