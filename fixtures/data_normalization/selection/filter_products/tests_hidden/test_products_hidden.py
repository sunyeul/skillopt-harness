from products import published_skus


def test_blank_skus_and_missing_status_are_skipped():
    assert published_skus(
        [{"sku": " "}, {"sku": "sku-1"}, {"sku": "sku-0", "status": "Published"}]
    ) == ["sku-0"]
