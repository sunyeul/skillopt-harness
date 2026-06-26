from categories import unique_categories


def test_unique_categories():
    assert unique_categories([" Support ", "sales", "support", "", "Sales "]) == [
        "support",
        "sales",
    ]
