from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True


class PaymentReceipt(BaseModel):
    id: int
    order_id: int
    file_path: str
    file_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    shipping_address: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None


class Order(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []
    receipts: List[PaymentReceipt] = []

    class Config:
        from_attributes = True
