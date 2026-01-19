from decimal import Decimal
from typing import Dict
import threading
from datetime import datetime

from common.datastore import (
    products_by_id,
    category_index,
    price_index,
    product_locks,
    carts,
)

from functions.feature3 import OrderProcessor
from functions.feature4 import search_by_price_range, search_by_category

# =========================
# PRODUCT OPERATIONS (UNCHANGED)
# =========================

def add_product(product_id: str, name: str, price: Decimal, stock: int, category: str):
    if product_id in products_by_id:
        print("❌ Product already exists")
        return

    products_by_id[product_id] = {
        "id": product_id,
        "name": name,
        "price": price,
        "stock": stock,
        "category": category,
        "reservations": {}
    }

    product_locks[product_id] = threading.Lock()

    category_index.setdefault(category, set()).add(product_id)
    price_index.append((price, product_id))
    price_index.sort()

    print("✅ Product added successfully")


def edit_product(product_id: str, name=None, price=None, stock=None, category=None):
    if product_id not in products_by_id:
        print("❌ Product not found")
        return

    product = products_by_id[product_id]

    with product_locks[product_id]:
        if name:
            product["name"] = name

        if price:
            old_price = product["price"]
            product["price"] = price
            price_index.remove((old_price, product_id))
            price_index.append((price, product_id))
            price_index.sort()

        if stock is not None:
            product["stock"] = stock

        if category:
            old_category = product["category"]
            category_index[old_category].discard(product_id)
            category_index.setdefault(category, set()).add(product_id)
            product["category"] = category

    print("✅ Product updated successfully")


def remove_product(product_id: str):
    if product_id not in products_by_id:
        print("❌ Product not found")
        return

    product = products_by_id[product_id]
    price_index.remove((product["price"], product_id))
    category_index[product["category"]].discard(product_id)

    del products_by_id[product_id]
    del product_locks[product_id]

    print("🗑️ Product removed successfully")


def view_products():
    if not products_by_id:
        print("📭 No products available")
        return

    print("\n📦 PRODUCT LIST")
    print("-" * 60)
    for p in products_by_id.values():
        print(
            f"ID: {p['id']} | "
            f"Name: {p['name']} | "
            f"Price: ₹{p['price']} | "
            f"Stock: {p['stock']} | "
            f"Category: {p['category']}"
        )
    print("-" * 60)


# =========================
# CART OPERATIONS (FEATURE 2)
# =========================

def add_to_cart(user_id: str, product_id: str, quantity: int):
    if quantity <= 0:
        print("❌ Invalid quantity")
        return

    product = products_by_id.get(product_id)
    if not product:
        print("❌ Product not found")
        return

    with product_locks[product_id]:
        reserved = product["reservations"].get(user_id, 0)
        total_reserved = sum(product["reservations"].values())
        available = product["stock"] - total_reserved

        if quantity > available:
            print("❌ Insufficient stock")
            return

        product["reservations"][user_id] = reserved + quantity

    carts.setdefault(user_id, {
        "user_id": user_id,
        "items": {},
        "created_at": datetime.utcnow(),
        "total_value": Decimal("0.00"),
    })

    cart = carts[user_id]
    cart["items"][product_id] = cart["items"].get(product_id, 0) + quantity
    cart["total_value"] += product["price"] * Decimal(quantity)

    print("✅ Added to cart")


def view_cart(user_id: str):
    cart = carts.get(user_id)
    if not cart or not cart["items"]:
        print("🛒 Cart is empty")
        return

    print("\n🛒 YOUR CART")
    print("-" * 50)
    for pid, qty in cart["items"].items():
        p = products_by_id[pid]
        print(f"{p['name']} | Qty: {qty} | ₹{p['price']} each")
    print("-" * 50)
    print(f"Total: ₹{cart['total_value']}")


# =========================
# MAIN MENU (ALL FEATURES)
# =========================

def main():
    order_processor = OrderProcessor()

    while True:
        print("""
=============================
 E-COMMERCE SYSTEM
=============================
1. Add Product
2. Edit Product
3. Remove Product
4. View Products
5. Add to Cart
6. View Cart
7. Search by Price
8. Search by Category
9. Checkout
10. View My Orders
11. Exit
""")

        choice = input("Select option: ").strip()

        if choice == "1":
            add_product(
                input("ID: "),
                input("Name: "),
                Decimal(input("Price: ")),
                int(input("Stock: ")),
                input("Category: ")
            )

        elif choice == "2":
            pid = input("Product ID: ")
            edit_product(
                pid,
                input("New name: ") or None,
                Decimal(input("New price: ")) if input else None,
                int(input("New stock: ")) if input else None,
                input("New category: ") or None
            )

        elif choice == "3":
            remove_product(input("Product ID: "))

        elif choice == "4":
            view_products()

        elif choice == "5":
            add_to_cart(
                input("User ID: "),
                input("Product ID: "),
                int(input("Quantity: "))
            )

        elif choice == "6":
            view_cart(input("User ID: "))

        elif choice == "7":
            ids = search_by_price_range(
                Decimal(input("Min price: ")),
                Decimal(input("Max price: "))
            )
            print("Results:", ids)

        elif choice == "8":
            ids = search_by_category(input("Category: "))
            print("Results:", ids)

        elif choice == "9":
            oid = order_processor.checkout(input("User ID: "))
            print("✅ Order placed:", oid if oid else "❌ Failed")

        elif choice == "10":
            user = input("User ID: ")
            for o in order_processor.get_orders_for_user(user):
                print(o)

        elif choice == "11":
            print("👋 Exiting")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
