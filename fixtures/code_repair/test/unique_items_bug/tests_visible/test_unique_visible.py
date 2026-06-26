from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unique import unique_items  # noqa: E402


def test_unique_normalizes_strings_and_skips_blanks():
    values = [" Apple ", "apple", "", "BANANA", " banana ", "  "]

    assert unique_items(values) == [" Apple ", "BANANA"]


def test_unique_supports_unhashable_values_without_mutation():
    values = [["a", 1], ["a", 1], {"x": [1, 2]}, {"x": [1, 2]}, " Tag ", "tag"]
    before = deepcopy(values)

    assert unique_items(values) == [["a", 1], {"x": [1, 2]}, " Tag "]
    assert values == before
