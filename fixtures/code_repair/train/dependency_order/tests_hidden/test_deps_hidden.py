import copy
import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
resolve_order = importlib.import_module("deps").resolve_order


def test_rejects_unknown_dependency_duplicate_name_and_cycle():
    with pytest.raises(ValueError):
        resolve_order({"app": ["missing"]})
    with pytest.raises(ValueError):
        resolve_order([{"name": "a", "deps": []}, {"name": "a", "deps": []}])
    with pytest.raises(ValueError):
        resolve_order({"a": ["b"], "b": ["a"]})


def test_does_not_mutate_input():
    items = [{"name": "b", "deps": ["a"]}, {"name": "a", "deps": []}]
    original = copy.deepcopy(items)
    assert resolve_order(items) == ["a", "b"]
    assert items == original


def test_list_ready_ties_use_priority_before_definition_order():
    assert resolve_order(
        [
            {"name": "slow", "deps": [], "priority": 5},
            {"name": "fast", "deps": [], "priority": -1},
            {"name": "later", "deps": ["fast"], "priority": -10},
        ]
    ) == ["fast", "later", "slow"]


def test_optional_dependencies_are_honored_only_when_present():
    assert resolve_order(
        [
            {"name": "app", "deps": ["?cache", "?missing"]},
            {"name": "cache", "deps": []},
        ]
    ) == ["cache", "app"]
