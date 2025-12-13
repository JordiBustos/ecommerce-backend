from pydantic import BaseModel, ConfigDict
from typing import Optional


class AddressBase(BaseModel):
    full_name: str
    country: str
    postal_code: str
    province: str
    city: str
    address_line1: str
    address_line2: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    full_name: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    phone_number: Optional[str] = None
    is_default: Optional[bool] = None


class Address(AddressBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
