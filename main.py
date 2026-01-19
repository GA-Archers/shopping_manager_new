from decimal import Decimal
from typing import Dict
import threading
from common.datastore import (
    products_by_id,
    category_index,
    price_index,
    product_locks
)

# =========================
# PRODUCT OPERATIONS
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
# MAIN MENU
# =========================

def main():
    while True:
        print("""
=============================
 PRODUCT MANAGEMENT SYSTEM
=============================
1. Add Product
2. Edit Product
3. Remove Product
4. View Products
5. Exit
""")

        choice = input("Select an option: ").strip()

        if choice == "1":
            pid = input("Product ID: ")
            name = input("Name: ")
            price = Decimal(input("Price: "))
            stock = int(input("Stock: "))
            category = input("Category: ")
            add_product(pid, name, price, stock, category)

        elif choice == "2":
            pid = input("Product ID to edit: ")
            print("Leave blank to skip updating a field")

            name = input("New Name: ").strip() or None
            price_input = input("New Price: ").strip()
            stock_input = input("New Stock: ").strip()
            category = input("New Category: ").strip() or None

            price = Decimal(price_input) if price_input else None
            stock = int(stock_input) if stock_input else None

            edit_product(pid, name, price, stock, category)

        elif choice == "3":
            pid = input("Product ID to remove: ")
            remove_product(pid)

        elif choice == "4":
            view_products()

        elif choice == "5":
            print("👋 Exiting Product Management System")
            break

        else:
            print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    main()
