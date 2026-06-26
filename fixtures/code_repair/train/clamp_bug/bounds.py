def allocate_capacity(requests, capacity):
    return {row["id"]: row["desired"] for row in requests}
