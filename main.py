from decimal import Decimal
from common.demo_db import load_demo_products
from functions.coreProduct import (
    add_product,
    get_product,
    update_stock
)

load_demo_products()

print(get_product("p1"))

add_product("p6", "Wooden Table", Decimal("15999"), 8, "furniture")
update_stock("p6", -3)

print(get_product("p6"))
