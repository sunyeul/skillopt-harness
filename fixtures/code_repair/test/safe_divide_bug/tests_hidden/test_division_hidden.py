from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from division import LRUCache  # noqa: E402


def test_get_missing_does_not_change_order_or_store_default():
    cache = LRUCache(2)
    cache.put("x", 1)
    assert cache.get("missing", 99) == 99
    cache.put("y", 2)
    assert cache.items() == [("x", 1), ("y", 2)]


def test_nonpositive_capacity_never_stores():
    cache = LRUCache(0)
    cache.put("x", 1)
    assert cache.get("x") is None
    assert cache.items() == []


def test_unhashable_keys_compare_by_structure_and_preserve_original_key():
    key = {"a": [1, 2]}
    equivalent = {"a": [1, 2]}
    cache = LRUCache(2)
    cache.put(key, "first")
    cache.put(["x"], "second")
    cache.put(equivalent, "updated")
    assert cache.get(key) == "updated"
    assert cache.items() == [(["x"], "second"), (key, "updated")]


def test_peek_does_not_update_recency():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.peek("a") == 1
    cache.put("c", 3)
    assert cache.items() == [("b", 2), ("c", 3)]
