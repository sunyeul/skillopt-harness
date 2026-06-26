from frequency import top_k_frequent


def test_k_larger_than_unique_count_and_first_seen_ties():
    assert top_k_frequent(["x", "y", "z", "y", "x"], 5) == ["x", "y", "z"]
