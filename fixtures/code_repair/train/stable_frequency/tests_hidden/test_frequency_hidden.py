from frequency import rank_labels


def test_ties_preserve_first_seen_order():
    assert rank_labels(["b", "a", "b", "a", "c"], 2) == ["b", "a"]


def test_limit_larger_than_unique_count():
    assert rank_labels(["x", "y", "x"], 5) == ["x", "y"]


def test_zero_limit_returns_empty_list():
    assert rank_labels(["x", "x"], 0) == []
