from products import published_skus


def test_published_skus():
    assert published_skus(
        [
            {"sku": "sku-2", "status": "PUBLISHED"},
            {"sku": "sku-1", "status": "draft"},
            {"sku": "sku-3", "status": "published"},
        ]
    ) == ["sku-2", "sku-3"]
