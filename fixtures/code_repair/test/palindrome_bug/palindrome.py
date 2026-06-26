def apply_line_patch(lines, operations):
    patched = list(lines)
    for operation in operations:
        if operation["op"] == "insert":
            patched.insert(operation["index"], operation["value"])
    return patched
