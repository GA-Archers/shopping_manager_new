from decimal import Decimal
from typing import Dict
from datetime import datetime

from common.datastore import (
    products_by_id,
    product_locks,
    carts,
)

# =========================
# SHOPPING CART OPERATIONS
# =========================

def add_to_cart(user_id: str, product_id: str, quantity: int) -> bool:
    """
    Add item to user's cart (creates cart if doesn't exist)
    Returns: True if added, False if insufficient stock or invalid product
    """
    if quantity <= 0:
        return False

    product = products_by_id.get(product_id)
    if not product:
        return False

    lock = product_locks[product_id]

    with lock:
        reserved = product["reservations"].get(user_id, 0)
        total_reserved = sum(product["reservations"].values())
        available_stock = product["stock"] - total_reserved

        if quantity > available_stock:
            return False

        # Reserve stock
        product["reservations"][user_id] = reserved + quantity

    # Create cart if not exists
    if user_id not in carts:
        carts[user_id] = {
            "user_id": user_id,
            "items": {},
            "created_at": datetime.utcnow(),
            "total_value": Decimal("0.00"),
        }

    cart = carts[user_id]

    # Update cart
    cart["items"][product_id] = cart["items"].get(product_id, 0) + quantity
    cart["total_value"] += product["price"] * Decimal(quantity)

    return True


def remove_from_cart(user_id: str, product_id: str) -> bool:
    """
    Remove item from cart
    Returns: True if removed, False if item not in cart
    """
    cart = carts.get(user_id)
    if not cart or product_id not in cart["items"]:
        return False

    product = products_by_id.get(product_id)
    if not product:
        return False

    quantity = cart["items"][product_id]
    lock = product_locks[product_id]

    with lock:
        # Release reservation
        product["reservations"][user_id] -= quantity
        if product["reservations"][user_id] == 0:
            del product["reservations"][user_id]

    # Update cart
    del cart["items"][product_id]
    cart["total_value"] -= product["price"] * Decimal(quantity)

    return True


def get_cart(user_id: str) -> Dict[str, int]:
    """
    Get all items in user's cart
    Returns: Dict {product_id: quantity}
    """
    cart = carts.get(user_id)
    if not cart:
        return {}

    # Return a copy to prevent external mutation
    return dict(cart["items"])
