from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from factorial import expand_ranges  # noqa: E402


def test_rejects_bad_segments_and_zero_step():
    for expr in ["", "1,,2", "a-b", "1-5:0", "1-5:-1", "5-1:1"]:
        with pytest.raises(ValueError):
            expand_ranges(expr)


def test_negative_numbers_and_first_seen_dedupe():
    assert expand_ranges("-2-2, -1, 2--2:-2") == [-2, -1, 0, 1, 2]


def test_dotdot_range_syntax_with_steps():
    assert expand_ranges("1..5:2, 5..1:-2") == [1, 3, 5]


def test_exclusion_segments_remove_seen_values_and_allow_readd():
    assert expand_ranges("1-5, !2..4, 3") == [1, 5, 3]
