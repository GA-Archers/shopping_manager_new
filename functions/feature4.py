from decimal import Decimal
from typing import List

from common.datastore import (
    price_index,
    category_index,
    products_by_id,
)

# =========================
# SEARCH AND FILTER
# =========================

def search_by_price_range(
    min_price: Decimal,
    max_price: Decimal
) -> List[str]:
    """
    Find all products in price range
    Returns: List of product_ids
    """
    if min_price > max_price:
        return []

    result: List[str] = []

    # price_index contains (price, product_id)
    for price, product_id in price_index:
        if price < min_price:
            continue
        if price > max_price:
            break
        # Ensure product still exists (safety)
        if product_id in products_by_id:
            result.append(product_id)

    return result


def search_by_category(category: str) -> List[str]:
    """
    Find all products in category
    Returns: List of product_ids
    """
    product_ids = category_index.get(category)
    if not product_ids:
        return []

    # Return a copy as a list to prevent external mutation
    return list(product_ids)
