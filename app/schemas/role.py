from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RoleBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class Role(RoleBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserWithRoles(BaseModel):
    """User schema with role information"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    roles: List[Role] = []
    
    class Config:
        from_attributes = True
