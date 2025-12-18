from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = relationship("Product", back_populates="brand")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    slug = Column(String, unique=True, index=True)
    image_url = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, nullable=True, index=True)
    ean = Column(String, unique=True, nullable=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    offer_price = Column(Float, nullable=True)  # Special offer price (lowest if set)
    stock = Column(Integer, default=0)
    is_always_in_stock = Column(Boolean, default=False)
    max_per_buy = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    units_per_package = Column(Integer, default=1)
    category_id = Column(Integer, ForeignKey("categories.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    image_url = Column(String)
    slug = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
