import threading
import uuid
from decimal import Decimal
from datetime import datetime
from typing import Dict, Optional, List

from common.datastore import (
    carts,
    products_by_id,
    product_locks,
    orders,
    user_orders,
)

class OrderProcessor:
    """
    Handles atomic checkout and order retrieval.
    """

    def __init__(self):
        # Ensures only one checkout mutates carts at a time
        self.checkout_lock = threading.Lock()

    def checkout(self, user_id: str) -> Optional[str]:
        """
        Converts user's cart into an order.
        Returns order_id if successful, None otherwise.
        """
        with self.checkout_lock:
            cart = carts.get(user_id)
            if not cart or not cart.get("items"):
                return None

            items = cart["items"]
            product_ids = sorted(items.keys())  # deadlock prevention

            try:
                # Acquire all required product locks
                for pid in product_ids:
                    product_locks[pid].acquire()

                # Validate stock against reservations
                for pid, qty in items.items():
                    product = products_by_id.get(pid)
                    if not product:
                        return None

                    reserved_for_user = product["reservations"].get(user_id, 0)
                    if reserved_for_user < qty:
                        return None

                # Deduct stock and clear reservations
                for pid, qty in items.items():
                    product = products_by_id[pid]
                    product["stock"] -= qty

                    # Remove reservation
                    del product["reservations"][user_id]

                # Calculate total
                total = self._calculate_total(items)

                # Create order
                order_id = self._create_order(user_id, items, total)

                # Clear cart
                del carts[user_id]

                return order_id

            finally:
                for pid in product_ids:
                    product_locks[pid].release()

    def _create_order(
        self,
        user_id: str,
        items: Dict[str, int],
        total: Decimal
    ) -> str:
        order_id = str(uuid.uuid4())

        order = {
            "order_id": order_id,
            "user_id": user_id,
            "items": items.copy(),
            "timestamp": datetime.utcnow(),
            "total": total,
            "status": "completed",
        }

        orders[order_id] = order
        user_orders.setdefault(user_id, []).append(order_id)

        return order_id

    def _calculate_total(self, items: Dict[str, int]) -> Decimal:
        total = Decimal("0.00")

        for pid, qty in items.items():
            total += products_by_id[pid]["price"] * Decimal(qty)

        return total

    def get_order(self, order_id: str) -> Optional[dict]:
        return orders.get(order_id)

    def get_orders_for_user(self, user_id: str) -> List[dict]:
        return [orders[oid] for oid in user_orders.get(user_id, [])]
