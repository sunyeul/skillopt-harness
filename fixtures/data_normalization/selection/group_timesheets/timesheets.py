def hours_by_employee(rows):
    return {row["employee_id"]: row["hours"] for row in rows}
