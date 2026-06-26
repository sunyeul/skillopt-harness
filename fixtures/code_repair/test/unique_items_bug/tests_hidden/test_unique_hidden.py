from unique import unique_items


def test_preserves_first_seen_order():
    assert unique_items(["b", "a", "b"]) == ["b", "a"]
