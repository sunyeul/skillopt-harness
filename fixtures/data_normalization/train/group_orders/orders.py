def totals_by_customer(orders):
    return {order["customer_id"]: order["amount"] for order in orders}
