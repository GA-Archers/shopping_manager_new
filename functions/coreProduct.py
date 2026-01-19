from decimal import Decimal
from typing import Optional
import threading
import bisect

from common.datastore import (
    products_by_id,
    category_index,
    price_index,
    product_locks
)

def add_product(
    product_id: str,
    name: str,
    price: Decimal,
    stock: int,
    category: str
) -> bool:
    """
    Add a new product to inventory
    Returns: True if added, False if product already exists
    """

    if product_id in products_by_id:
        return False

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

    bisect.insort(price_index, (price, product_id))

    return True


def get_product(product_id: str) -> Optional[dict]:
    """
    Retrieve product details
    Returns: Product dict or None if not found
    """

    return products_by_id.get(product_id)


def update_stock(product_id: str, quantity: int) -> bool:
    """
    Update product stock (positive or negative)
    Returns: True if updated, False if product not found or insufficient stock
    """

    product = products_by_id.get(product_id)
    if not product:
        return False

    lock = product_locks.get(product_id)
    if not lock:
        return False

    with lock:
        new_stock = product["stock"] + quantity
        if new_stock < 0:
            return False

        product["stock"] = new_stock

    return True
