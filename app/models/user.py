from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.favorite import user_favorites
from app.models.price_list import price_list_users
from app.models.role import user_roles


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    dni = Column(String, unique=True, nullable=True, index=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    favorite_products = relationship("Product", secondary=user_favorites, backref="favorited_by")
    price_lists = relationship("PriceList", secondary=price_list_users, back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    coupons = relationship("Coupon", secondary="coupon_users", back_populates="assigned_users")
    
    def has_role(self, role_slug: str) -> bool:
        """Check if user has a specific role by slug"""
        return any(role.slug == role_slug for role in self.roles)
    
    def has_any_role(self, role_slugs: list[str]) -> bool:
        """Check if user has any of the specified roles"""
        return any(self.has_role(slug) for slug in role_slugs)
    
    def has_all_roles(self, role_slugs: list[str]) -> bool:
        """Check if user has all of the specified roles"""
        return all(self.has_role(slug) for slug in role_slugs)
