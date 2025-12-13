from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class PriceListItemBase(BaseModel):
    product_id: int
    price: float


class PriceListItemCreate(PriceListItemBase):
    pass


class PriceListItemUpdate(BaseModel):
    price: Optional[float] = None


class PriceListItem(PriceListItemBase):
    id: int
    price_list_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PriceListBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    role_filter: Optional[str] = None


class PriceListCreate(PriceListBase):
    pass


class PriceListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    role_filter: Optional[str] = None


class PriceList(PriceListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    price_list_items: List[PriceListItem] = []
    
    model_config = ConfigDict(from_attributes=True)


class PriceListWithUsers(PriceList):
    user_ids: List[int] = []
    
    model_config = ConfigDict(from_attributes=True)
