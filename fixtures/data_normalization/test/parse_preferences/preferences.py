def preference_flags(rows):
    return {row["name"]: bool(row.get("value")) for row in rows}
