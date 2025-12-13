from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.cart import Cart, CartItemCreate, CartItemUpdate
from app.services.cart import CartService

router = APIRouter()


@router.get("/", response_model=Cart)
def get_cart(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get current user's shopping cart"""
    return CartService.get_user_cart(db, current_user)


@router.post("/items", response_model=Cart, status_code=201)
def add_to_cart(
    item_in: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add item to cart"""
    return CartService.add_item_to_cart(db, current_user, item_in)


@router.put("/items/{item_id}", response_model=Cart)
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update cart item quantity"""
    return CartService.update_cart_item(db, current_user, item_id, item_in)


@router.delete("/items/{item_id}", status_code=204)
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove item from cart"""
    CartService.remove_item_from_cart(db, current_user, item_id)
    return None


@router.delete("/", status_code=204)
def clear_cart(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    CartService.clear_cart(db, current_user)
    return None
