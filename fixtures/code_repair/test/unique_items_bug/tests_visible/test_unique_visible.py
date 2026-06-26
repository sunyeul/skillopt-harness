from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unique import StablePriorityQueue  # noqa: E402


def test_priority_then_original_insertion_order():
    queue = StablePriorityQueue()
    queue.push("second", 5)
    queue.push("first", 1)
    queue.push("third", 5)
    assert len(queue) == 3
    assert [queue.pop(), queue.pop(), queue.pop()] == ["first", "second", "third"]


def test_updating_existing_item_keeps_original_tie_order():
    queue = StablePriorityQueue()
    queue.push("a", 10)
    queue.push("b", 10)
    queue.push("a", 10)
    assert [queue.pop(), queue.pop()] == ["a", "b"]


def test_peek_remove_and_structural_items_are_part_of_contract():
    queue = StablePriorityQueue()
    first = {"role": ["admin"]}
    equivalent = {"role": ["admin"]}
    queue.push(first, 5)
    queue.push(["other"], 5)
    queue.push(equivalent, 1)
    assert queue.peek() is first
    assert len(queue) == 2
    assert queue.pop() is first
    assert queue.remove(["other"]) is True
    assert queue.remove("missing") is False
