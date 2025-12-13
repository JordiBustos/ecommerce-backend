from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.product import Product


class CartItemBase(BaseModel):
    product_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int


class CartItem(CartItemBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    product: Product

    class Config:
        from_attributes = True


class Cart(BaseModel):
    items: List[CartItem]
    total: float
