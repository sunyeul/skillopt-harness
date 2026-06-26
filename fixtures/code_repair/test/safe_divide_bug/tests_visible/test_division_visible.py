from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from division import LRUCache  # noqa: E402


def test_put_get_and_lru_eviction():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b", "missing") == "missing"
    assert cache.items() == [("a", 1), ("c", 3)]


def test_update_existing_marks_recent_without_growing():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    cache.put("c", 3)
    assert cache.items() == [("a", 10), ("c", 3)]


def test_peek_capacity_and_structural_keys_are_part_of_contract():
    cache = LRUCache(0)
    cache.put("ignored", 1)
    assert cache.items() == []

    key = {"role": ["admin"]}
    equivalent = {"role": ["admin"]}
    cache = LRUCache(2)
    cache.put(key, "first")
    cache.put(["other"], "second")
    cache.put(equivalent, "updated")
    assert cache.peek(key) == "updated"
    cache.put("third", 3)
    assert cache.items() == [(key, "updated"), ("third", 3)]
