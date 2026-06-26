from categories import unique_categories


def test_blank_categories_are_skipped():
    assert unique_categories(["", " "]) == []
