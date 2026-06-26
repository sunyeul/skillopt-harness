import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
rank_labels = importlib.import_module("frequency").rank_labels


def test_rank_labels_normalizes_counts_and_preserves_first_seen_ties():
    labels = [" Red ", "blue", "red", "", "BLUE", "green"]

    assert rank_labels(labels, 3) == ["red", "blue", "green"]
    assert labels == [" Red ", "blue", "red", "", "BLUE", "green"]
