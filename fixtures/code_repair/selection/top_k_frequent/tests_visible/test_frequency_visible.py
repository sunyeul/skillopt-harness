from frequency import top_k_frequent


def test_frequency_order_and_ties():
    assert top_k_frequent(["b", "a", "b", "c", "a", "b"], 2) == ["b", "a"]
