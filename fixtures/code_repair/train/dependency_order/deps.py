def resolve_order(items):
    if isinstance(items, dict):
        return list(items)
    return [item["name"] for item in items]
