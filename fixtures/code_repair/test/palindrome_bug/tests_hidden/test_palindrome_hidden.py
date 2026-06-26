from pathlib import Path
import copy
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from palindrome import apply_line_patch  # noqa: E402


def test_rejects_invalid_operations_without_mutation():
    lines = ["a", "b"]
    operations = [{"op": "delete", "index": 1, "count": 2}]
    original_ops = copy.deepcopy(operations)
    with pytest.raises(ValueError):
        apply_line_patch(lines, operations)
    assert lines == ["a", "b"]
    assert operations == original_ops


def test_replace_with_multiple_values_and_delete_count():
    assert apply_line_patch(
        ["a", "b", "c", "d"],
        [
            {"op": "replace", "index": 1, "count": 2, "value": ["x", "y", "z"]},
            {"op": "delete", "index": 3, "count": 1},
        ],
    ) == ["a", "x", "y", "d"]


def test_rejects_unknown_op_and_negative_index():
    for operation in [{"op": "unknown", "index": 0}, {"op": "insert", "index": -1, "value": "x"}]:
        with pytest.raises(ValueError):
            apply_line_patch([], [operation])


def test_move_uses_target_index_after_removal():
    assert apply_line_patch(
        ["a", "b", "c", "d", "e"],
        [{"op": "move", "index": 1, "count": 2, "target_index": 3}],
    ) == ["a", "d", "e", "b", "c"]


def test_copy_inserts_block_without_removing_original():
    assert apply_line_patch(
        ["a", "b", "c"],
        [{"op": "copy", "index": 0, "count": 2, "target_index": 3}],
    ) == ["a", "b", "c", "a", "b"]
