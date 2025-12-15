from sqlalchemy import Column, Integer, String, JSON, Float
from app.db.base import Base


class Store(Base):
    __tablename__ = "store_settings"

    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String, nullable=False, default="My Store")
    
    # Branding
    primary_color = Column(String, nullable=False, default="#3B82F6")
    secondary_color = Column(String, nullable=False, default="#10B981")
    accent_color = Column(String, nullable=True, default="#F59E0B")
    logo_url = Column(String, nullable=True)
    
    # Contact Information
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Physical Address
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Business Information
    opening_hours = Column(JSON, nullable=True)  # {"monday": {"open": "09:00", "close": "18:00"}, ...}
    description = Column(String, nullable=True)
    tax_rate = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="EUR")
    
    # Social Media
    facebook_url = Column(String, nullable=True)
    instagram_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    
    # Payment Information
    bank_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    cbu = Column(String, nullable=True)  # Clave Bancaria Uniforme (Argentina)
    cvu = Column(String, nullable=True)  # Clave Virtual Uniforme (Argentina)
    alias = Column(String, nullable=True)  # Bank alias (Argentina)
    account_holder_name = Column(String, nullable=True)
    account_type = Column(String, nullable=True)  # checking, savings, etc.
    swift_code = Column(String, nullable=True)  # For international transfers
    payment_instructions = Column(String, nullable=True)  # Additional payment notes