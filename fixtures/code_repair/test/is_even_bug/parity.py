def reconcile_status(events):
    return {event["id"]: event["status"] for event in events}
