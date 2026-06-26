from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unique import unique_items  # noqa: E402


def test_unique_preserves_first_seen_output_representation():
    values = ["  One", "one  ", {"b": 2, "a": 1}, {"a": 1, "b": 2}, [1, 2], [1, 2]]
    result = unique_items(values)

    assert result == ["  One", {"b": 2, "a": 1}, [1, 2]]
    assert list(result[1].keys()) == ["b", "a"]


def test_unique_skips_blank_strings_and_does_not_mutate_nested_values():
    values = ["", "\t", {"k": [1, 2]}, {"k": [1, 2]}, " Echo ", "echo"]
    before = deepcopy(values)

    assert unique_items(values) == [{"k": [1, 2]}, " Echo "]
    assert values == before
