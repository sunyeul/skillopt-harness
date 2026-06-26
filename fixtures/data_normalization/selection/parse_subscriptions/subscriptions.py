def subscription_flags(rows):
    return {row["plan"]: bool(row.get("enabled")) for row in rows}
