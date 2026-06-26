from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from palindrome import apply_line_patch  # noqa: E402


def test_applies_insert_delete_and_replace_sequentially():
    lines = ["a", "b", "c"]
    assert apply_line_patch(
        lines,
        [
            {"op": "insert", "index": 1, "value": ["x", "y"]},
            {"op": "delete", "index": 3},
            {"op": "replace", "index": 0, "count": 2, "value": "z"},
        ],
    ) == ["z", "y", "c"]
    assert lines == ["a", "b", "c"]


def test_insert_at_end():
    assert apply_line_patch(["a"], [{"op": "insert", "index": 1, "value": "b"}]) == ["a", "b"]
