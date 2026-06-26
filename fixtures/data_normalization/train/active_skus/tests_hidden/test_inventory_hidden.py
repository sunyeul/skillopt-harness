from inventory import active_skus


def test_missing_status_and_blank_sku_are_skipped():
    assert active_skus(
        [
            {"sku": "x-1"},
            {"sku": " ", "status": "active"},
            {"sku": "a-1", "status": "Active"},
        ]
    ) == ["a-1"]
