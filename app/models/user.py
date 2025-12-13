from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.favorite import user_favorites
from app.models.price_list import price_list_users


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
