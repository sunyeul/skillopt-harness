import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
resolve_order = importlib.import_module("deps").resolve_order


def test_mapping_dependencies_before_dependents_with_stable_ready_order():
    assert resolve_order(
        {
            "app": ["db", "cache"],
            "db": [],
            "cache": ["config"],
            "config": [],
        }
    ) == ["db", "config", "cache", "app"]


def test_list_items_and_duplicate_dependencies():
    assert resolve_order(
        [
            {"name": "lint", "deps": ["install", "install"]},
            {"name": "test", "deps": ["install"]},
            {"name": "install", "deps": []},
        ]
    ) == ["install", "lint", "test"]
