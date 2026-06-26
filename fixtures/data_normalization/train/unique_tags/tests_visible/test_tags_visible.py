from tags import unique_tags


def test_unique_tags_first_seen_order():
    assert unique_tags([" Bug ", "feature", "bug", "", "Feature "]) == [
        "bug",
        "feature",
    ]
