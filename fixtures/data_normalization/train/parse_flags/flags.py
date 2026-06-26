def normalize_flags(rows):
    return {row["key"]: bool(row.get("value")) for row in rows}
