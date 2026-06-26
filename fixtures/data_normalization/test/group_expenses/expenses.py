def totals_by_project(expenses):
    return {expense["project_id"]: expense["amount"] for expense in expenses}
