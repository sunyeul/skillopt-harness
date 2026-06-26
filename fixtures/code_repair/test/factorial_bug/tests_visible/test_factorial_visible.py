from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from factorial import expand_ranges  # noqa: E402


def test_expands_single_values_ranges_and_dedupes():
    assert expand_ranges("1, 3-5, 4, 7-5") == [1, 3, 4, 5, 7, 6]


def test_explicit_step_and_whitespace():
    assert expand_ranges(" 10-4:-3, 2-8:3 ") == [10, 7, 4, 2, 5, 8]
