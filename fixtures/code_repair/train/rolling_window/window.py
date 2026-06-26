def rolling_totals(readings, window):
    return [{"count": len(readings), "total": sum(readings), "average": sum(readings) / len(readings)}]
