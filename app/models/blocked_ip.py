from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import Base


class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True, nullable=False)  # IPv4 or IPv6
    reason = Column(String(255), nullable=False)  # Why it was blocked
    blocked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    blocked_until = Column(DateTime(timezone=True), nullable=True)  # NULL = permanent
    is_active = Column(Boolean, default=True, nullable=False)
    blocked_by = Column(String(50), default="system", nullable=False)  # system/admin/auto
    notes = Column(Text, nullable=True)
    violation_count = Column(Integer, default=1, nullable=False)  # How many violations led to block
