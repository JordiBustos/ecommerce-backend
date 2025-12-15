from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Dict
from datetime import datetime


class PhysicalStoreBase(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    opening_hours: Optional[Dict[str, dict]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True


class PhysicalStoreCreate(PhysicalStoreBase):
    pass


class PhysicalStoreUpdate(BaseModel):
    name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    opening_hours: Optional[Dict[str, dict]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: Optional[bool] = None


class PhysicalStore(PhysicalStoreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
