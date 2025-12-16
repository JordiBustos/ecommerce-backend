from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


# Many-to-many relationship table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)


class Role(Base):
    """
    Role model for user access control.
    Supports multiple roles per user for flexible permissions.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")


# Default roles for e-commerce system
DEFAULT_ROLES = [
    {
        "name": "End Consumer",
        "slug": "end-consumer",
        "description": "Regular customer purchasing for personal use"
    },
    {
        "name": "Wholesale",
        "slug": "wholesale",
        "description": "Wholesale buyer with special pricing and bulk purchase capabilities"
    },
    {
        "name": "Distributor",
        "slug": "distributor",
        "description": "Authorized distributor with extended credit terms and volume discounts"
    },
    {
        "name": "Retail Partner",
        "slug": "retail-partner",
        "description": "Retail business partner with special terms and conditions"
    },
    {
        "name": "VIP Customer",
        "slug": "vip-customer",
        "description": "VIP customer with exclusive benefits and priority service"
    },
    {
        "name": "Corporate",
        "slug": "corporate",
        "description": "Corporate account for business purchases with invoicing"
    },
    {
        "name": "Guest",
        "slug": "guest",
        "description": "Temporary role for browsing without full registration"
    }
]
