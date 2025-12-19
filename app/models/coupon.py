from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


# Association table for many-to-many relationship between coupons and users
coupon_users = Table(
    'coupon_users',
    Base.metadata,
    Column('coupon_id', Integer, ForeignKey('coupons.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Discount configuration
    discount_type = Column(Enum(DiscountType), nullable=False, default=DiscountType.PERCENTAGE)
    discount_value = Column(Float, nullable=False)  # Percentage (0-100) or fixed amount
    
    # Conditions
    min_order_amount = Column(Float, nullable=True, default=0)  # Minimum order total to apply discount
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # Null = unlimited uses
    current_uses = Column(Integer, default=0, nullable=False)
    max_uses_per_user = Column(Integer, nullable=True, default=1)
    
    # Validity
    is_active = Column(Boolean, default=True, nullable=False)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assigned_users = relationship("User", secondary=coupon_users, back_populates="coupons")
    
    def is_valid(self) -> bool:
        """Check if coupon is currently valid"""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_to and now > self.valid_to:
            return False
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def can_be_used_by_user(self, user_id: int, db) -> bool:
        """Check if user can use this coupon"""
        # If coupon has assigned users, check if user is in the list
        if self.assigned_users:
            user_ids = [u.id for u in self.assigned_users]
            if user_id not in user_ids:
                return False
        
        # Check per-user usage limit
        if self.max_uses_per_user:
            from app.models.order import Order
            usage_count = db.query(Order).filter(
                Order.user_id == user_id,
                Order.coupon_id == self.id
            ).count()
            
            if usage_count >= self.max_uses_per_user:
                return False
        
        return True
    
    def calculate_discount(self, order_total: float) -> float:
        """Calculate discount amount based on order total"""
        if order_total < self.min_order_amount:
            return 0.0
        
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (order_total * self.discount_value) / 100
        else:
            discount = self.discount_value
        
        # Discount cannot exceed order total
        return min(discount, order_total)
