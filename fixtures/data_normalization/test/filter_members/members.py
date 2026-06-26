def active_member_ids(members):
    return [member["id"] for member in members if member.get("status") == "active"]
