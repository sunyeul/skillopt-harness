from intervals import merge_intervals


def test_unsorted_touching_intervals_merge():
    assert merge_intervals([[5, 7], [1, 3], [3, 4]]) == [[1, 4], [5, 7]]
