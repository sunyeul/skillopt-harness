def active_skus(items):
    return [item["sku"] for item in items if item.get("status") == "active"]
