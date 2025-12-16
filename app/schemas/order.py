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
    shipping_address: Optional[str] = None  # Deprecated
    address_id: Optional[int] = None
    physical_store_id: Optional[int] = None
    replacement_criterion: Optional[str] = None
    comment: Optional[str] = None


class OrderCreate(BaseModel):
    address_id: Optional[int] = None  # For delivery to address
    physical_store_id: Optional[int] = None  # For pickup at store
    items: List[OrderItemCreate]
    replacement_criterion: Optional[str] = None
    comment: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    replacement_criterion: Optional[str] = None
    comment: Optional[str] = None
    estimated_delivery_date: Optional[datetime] = None


class Order(OrderBase):
    id: int
    user_id: int
    address_id: Optional[int] = None
    physical_store_id: Optional[int] = None
    total_amount: float
    status: OrderStatus
    payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    estimated_delivery_date: Optional[datetime] = None
    
    # Address snapshot fields
    snapshot_full_name: Optional[str] = None
    snapshot_country: Optional[str] = None
    snapshot_postal_code: Optional[str] = None
    snapshot_province: Optional[str] = None
    snapshot_city: Optional[str] = None
    snapshot_address_line1: Optional[str] = None
    snapshot_address_line2: Optional[str] = None
    snapshot_phone_number: Optional[str] = None
    
    items: List[OrderItem] = []
    receipts: List[PaymentReceipt] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Response model for paginated orders list"""
    orders: List[Order]
    total: int
