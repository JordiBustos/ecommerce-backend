from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_active_user, get_current_superuser
from app.db.base import get_db
from app.models.user import User
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate
from app.services.order import OrderService

router = APIRouter()


@router.post("/", response_model=OrderSchema, status_code=201)
def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new order"""
    return OrderService.create_order(db, current_user, order_in)


@router.get("/", response_model=List[OrderSchema])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current user's orders"""
    return OrderService.get_user_orders(db, current_user, skip, limit)


@router.get("/{order_id}", response_model=OrderSchema)
def read_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get specific order details"""
    return OrderService.get_user_order(db, current_user, order_id)


@router.put("/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update order status (admin only)"""
    return OrderService.update_order(db, order_id, order_in, current_user)


@router.get("/all/admin", response_model=List[OrderSchema])
def read_all_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Get all orders (admin only)"""
    return OrderService.get_all_orders(db, current_user, skip, limit)
