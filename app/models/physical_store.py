from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from datetime import datetime
from app.db.base import Base


class PhysicalStore(Base):
    __tablename__ = "physical_stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    opening_hours = Column(JSON, nullable=True)  # {"monday": {"open": "09:00", "close": "18:00"}, ...}
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
