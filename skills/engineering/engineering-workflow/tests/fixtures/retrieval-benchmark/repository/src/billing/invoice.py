def calculate_invoice_total(line_items):
    return sum(item.amount for item in line_items)
