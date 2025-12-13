from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict


class OpeningHours(BaseModel):
    open: Optional[str] = None
    close: Optional[str] = None
    closed: bool = False


class StoreBase(BaseModel):
    store_name: str
    primary_color: str
    secondary_color: str
    accent_color: Optional[str] = None
    logo_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    opening_hours: Optional[Dict[str, dict]] = None
    description: Optional[str] = None
    tax_rate: float = 0.0
    currency: str = "EUR"
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    logo_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    opening_hours: Optional[Dict[str, dict]] = None
    description: Optional[str] = None
    tax_rate: Optional[float] = None
    currency: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class Store(StoreBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
