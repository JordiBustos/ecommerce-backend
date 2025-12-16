from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime, date
from app.core.honeypot import HoneypotMixin
from app.core.input_validation import InputSanitizer, validate_password_strength


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    dni: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str, info: ValidationInfo) -> str:
        return InputSanitizer.sanitize_string(v, max_length=50)

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v:
            return InputSanitizer.sanitize_string(v, max_length=100)
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v:
            return InputSanitizer.sanitize_phone(v)
        return v


class UserCreate(UserBase, HoneypotMixin):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str, info: ValidationInfo) -> str:
        validate_password_strength(v)
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    dni: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserWithRoles(UserInDB):
    """User schema with role information"""
    roles: List["Role"] = []
    
    class Config:
        from_attributes = True


# Import Role here to avoid circular import issues
from app.schemas.role import Role
UserWithRoles.model_rebuild()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
