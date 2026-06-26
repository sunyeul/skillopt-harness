def published_skus(products):
    return [product["sku"] for product in products if product.get("status") == "published"]
