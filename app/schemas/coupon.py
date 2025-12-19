from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from app.models.coupon import DiscountType


class CouponBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    min_order_amount: float = Field(default=0, ge=0)
    max_uses: Optional[int] = Field(None, ge=1)
    max_uses_per_user: Optional[int] = Field(default=1, ge=1)
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None

    @validator("discount_value")
    def validate_discount_value(cls, v, values):
        if "discount_type" in values:
            if values["discount_type"] == DiscountType.PERCENTAGE:
                if v > 100:
                    raise ValueError("Percentage discount cannot exceed 100%")
        return v

    @validator("valid_to")
    def validate_dates(cls, v, values):
        if v and "valid_from" in values and values["valid_from"]:
            if v <= values["valid_from"]:
                raise ValueError("valid_to must be after valid_from")
        return v


class CouponCreate(CouponBase):
    assigned_user_ids: Optional[List[int]] = Field(default_factory=list)


class CouponUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, gt=0)
    min_order_amount: Optional[float] = Field(None, ge=0)
    max_uses: Optional[int] = Field(None, ge=1)
    max_uses_per_user: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    assigned_user_ids: Optional[List[int]] = None

    @validator("discount_value")
    def validate_discount_value(cls, v, values):
        if v and "discount_type" in values and values["discount_type"]:
            if values["discount_type"] == DiscountType.PERCENTAGE:
                if v > 100:
                    raise ValueError("Percentage discount cannot exceed 100%")
        return v


class CouponUserInfo(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]

    class Config:
        from_attributes = True


class CouponResponse(CouponBase):
    id: int
    current_uses: int
    created_at: datetime
    updated_at: datetime
    assigned_users: List[CouponUserInfo] = []

    class Config:
        from_attributes = True


class CouponApply(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)


class CouponValidationResponse(BaseModel):
    valid: bool
    message: Optional[str] = None
    discount_amount: Optional[float] = None
    coupon: Optional[CouponResponse] = None


class CouponListResponse(BaseModel):
    coupons: List[CouponResponse]
    total: int
