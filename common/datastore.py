from typing import Dict, List, Set, Tuple, Optional
from decimal import Decimal
from datetime import datetime
import threading
# =========================
# PRODUCT CATALOG
# =========================

products_by_id: Dict[str, dict] = {}
category_index: Dict[str, Set[str]] = {}
price_index: List[Tuple[Decimal, str]] = []

# =========================
# INVENTORY & CONCURRENCY
# =========================s

product_locks: Dict[str, threading.Lock] = {}

# =========================
# CART MANAGEMENT
# =========================

carts: Dict[str, dict] = {}

# =========================
# ORDERS
# =========================

orders: Dict[str, dict] = {}
user_orders: Dict[str, List[str]] = {}

# Product Schema
# {
#   "id": str,
#   "name": str,
#   "price": Decimal,
#   "stock": int,
#   "category": str,
#   "reservations": Dict[user_id, quantity]
# }

# Cart Schema
# {
#   "user_id": str,
#   "items": Dict[product_id, quantity],
#   "created_at": datetime,
#   "total_value": Decimal
# }

# Order Schema
# {
#   "order_id": str,
#   "user_id": str,
#   "items": Dict[product_id, quantity],
#   "timestamp": datetime,
#   "total": Decimal,
#   "status": str
# }