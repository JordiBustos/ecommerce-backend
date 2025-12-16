from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    products,
    cart,
    orders,
    addresses,
    price_lists,
    favorites,
    best_selling_products,
    store,
    newsletter,
    roles,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
api_router.include_router(
    price_lists.router, prefix="/price-lists", tags=["price-lists"]
)
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(
    best_selling_products.router, prefix="/best-selling", tags=["best-selling"]
)
api_router.include_router(store.router, prefix="/store", tags=["store"])
api_router.include_router(newsletter.router, prefix="/newsletter", tags=["newsletter"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
