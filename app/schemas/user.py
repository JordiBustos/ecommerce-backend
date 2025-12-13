from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    dni: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
