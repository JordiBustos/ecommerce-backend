from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.product import Product
from app.services.favorite import FavoriteService

router = APIRouter()


@router.get("/", response_model=List[Product])
def get_user_favorites(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all favorite products for the current user"""
    return FavoriteService.get_user_favorites(db, current_user.id)


@router.post("/{product_id}")
def add_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a product to favorites"""
    return FavoriteService.add_favorite(db, current_user.id, product_id)


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a product from favorites"""
    return FavoriteService.remove_favorite(db, current_user.id, product_id)
