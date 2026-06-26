from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unique import StablePriorityQueue  # noqa: E402


def test_update_changes_priority_without_changing_first_order():
    queue = StablePriorityQueue()
    queue.push("a", 5)
    queue.push("b", 1)
    queue.push("a", 1)
    assert [queue.pop(), queue.pop()] == ["a", "b"]


def test_remove_and_empty_pop():
    queue = StablePriorityQueue()
    queue.push("x", 1)
    assert queue.remove("missing") is False
    assert queue.remove("x") is True
    assert len(queue) == 0
    with pytest.raises(IndexError):
        queue.pop()


def test_unhashable_items_compare_structurally_and_preserve_original_item():
    queue = StablePriorityQueue()
    first = {"a": [1, 2]}
    equivalent = {"a": [1, 2]}
    queue.push(first, 5)
    queue.push(["later"], 5)
    queue.push(equivalent, 1)
    assert queue.pop() is first
    assert queue.remove(["later"]) is True
    assert len(queue) == 0


def test_peek_returns_next_item_without_removing_it():
    queue = StablePriorityQueue()
    queue.push("a", 2)
    queue.push("b", 1)
    assert queue.peek() == "b"
    assert len(queue) == 2
    assert queue.pop() == "b"
