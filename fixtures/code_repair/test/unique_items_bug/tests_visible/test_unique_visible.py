from unique import unique_items


def test_removes_duplicates():
    assert unique_items([1, 1, 2]) == [1, 2]
