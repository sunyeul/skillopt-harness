from inventory import active_skus


def test_active_skus_sorted_and_normalized():
    assert active_skus(
        [
            {"sku": " b-2 ", "status": "ACTIVE"},
            {"sku": "a-1", "status": "inactive"},
            {"sku": " c-3 ", "status": "active"},
        ]
    ) == ["b-2", "c-3"]
