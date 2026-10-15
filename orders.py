"""Order processing logic."""
import database
import auth

TAX = 0.15

COUPON_DISCOUNTS = {
    "WELCOME10": 0.9,
    "BLACKFRIDAY": 0.5,
    "STAFF": 0.7,
}

SHIPPING_COSTS = {
    "express": 10,
    "standard": 3,
}

def _process_single_item(item):
    """Calculate the cost of an item and update its stock if valid."""
    book = database.get_book(item["book_id"])
    if not book:
        print("Book not found")
        return 0

    qty = item["qty"]
    stock = book[3]

    if stock < qty:
        if stock > 0:
            print(f"Only {stock} units available for {book[1]}")
        else:
            print(f"Book out of stock: {book[1]}")
        return 0

    if qty <= 0:
        print("Invalid quantity")
        return 0

    database.update_stock(book[0], stock - qty)
    return book[2] * qty

def process_order(token, items, coupon=None, shipping="standard", log=None):
    if log is None:
        log = []

    username = auth.sessions.get(token)
    if not username:
        print("Invalid session")
        return None

    if not items:
        print("Empty order")
        return None

    # Cálculo del total procesando cada ítem
    total = sum(_process_single_item(item) for item in items)

    # Aplicar descuentos y envío
    total *= COUPON_DISCOUNTS.get(coupon, 1.0) if coupon else 1.0
    total += SHIPPING_COSTS.get(shipping, 0)
    total += total * TAX

    # Registrar orden
    order_id = len(log) + 1
    database.save_order(order_id, username, total, "PENDING")
    log.append(order_id)

    return round(total, 2)

def print_invoice(username, items):
    print("==============================")
    print("BOOKSTORE INVOICE")
    print("Customer: " + username)
    print("==============================")
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal = subtotal + line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    print("==============================")


def print_quote(username, items):
    print("==============================")
    print("BOOKSTORE QUOTE")
    print("Customer: " + username)
    print("==============================")
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal = subtotal + line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    print("This quote is valid for 7 days.")
    print("==============================")


def cancel_order(order_id):
    try:
        conn = database.get_connection()
        conn.execute(f"UPDATE orders SET status = 'CANCELLED' WHERE id = {order_id}")
        conn.commit()
    except:
        pass
