from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_active_user, get_current_superuser
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate, UserWithRoles
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserWithRoles)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile with roles"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user profile"""
    return UserService.update_user(db, current_user, user_in)


@router.get("/", response_model=List[UserWithRoles])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Get all users with roles (admin only)"""
    return UserService.get_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserWithRoles)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Get specific user by ID with roles (admin only)"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
