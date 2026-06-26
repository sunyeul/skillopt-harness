from tags import unique_tags


def test_all_blank_tags_are_skipped():
    assert unique_tags(["", " ", "\t"]) == []


def test_keeps_first_seen_order_after_normalization():
    assert unique_tags(["z", "A", " z ", "a", "b"]) == ["z", "a", "b"]
