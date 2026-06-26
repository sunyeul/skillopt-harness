from intervals import merge_intervals


def test_negative_and_nested_intervals():
    assert merge_intervals([[10, 12], [-3, -1], [-2, 5], [11, 11]]) == [[-3, 5], [10, 12]]
