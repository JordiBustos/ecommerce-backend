from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True)
    physical_store_id = Column(Integer, ForeignKey("physical_stores.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    shipping_address = Column(String, nullable=True)  # Deprecated, keeping for backward compatibility
    payment_id = Column(String)
    replacement_criterion = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    
    # Address snapshot at order time (preserves data if user changes address later)
    snapshot_full_name = Column(String, nullable=True)
    snapshot_country = Column(String, nullable=True)
    snapshot_postal_code = Column(String, nullable=True)
    snapshot_province = Column(String, nullable=True)
    snapshot_city = Column(String, nullable=True)
    snapshot_address_line1 = Column(String, nullable=True)
    snapshot_address_line2 = Column(String, nullable=True)
    snapshot_phone_number = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estimated_delivery_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    address = relationship("Address")
    physical_store = relationship("PhysicalStore")
    items = relationship("OrderItem", back_populates="order")
    receipts = relationship("PaymentReceipt", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class PaymentReceipt(Base):
    __tablename__ = "payment_receipts"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    file_path = Column(String, nullable=False)  # Path to receipt file (image or PDF)
    file_type = Column(String, nullable=False)  # MIME type of the file
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="receipts")
