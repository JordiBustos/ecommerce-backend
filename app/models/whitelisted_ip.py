from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base


class WhitelistedIP(Base):
    __tablename__ = "whitelisted_ips"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True, nullable=False)  # IPv4 or IPv6
    description = Column(String(255), nullable=False)  # What/who this IP is for
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    added_by = Column(String(50), default="admin", nullable=False)  # admin/system
    notes = Column(Text, nullable=True)
