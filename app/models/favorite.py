from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from datetime import datetime
from app.db.base import Base


user_favorites = Table(
    'user_favorites',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)
