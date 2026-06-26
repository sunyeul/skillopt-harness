from frequency import rank_labels


def test_frequency_order():
    assert rank_labels(["red", "blue", "red", "green", "blue", "red"], 2) == [
        "red",
        "blue",
    ]
