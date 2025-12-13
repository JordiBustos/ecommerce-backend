from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.schemas.price_list import (
    PriceList,
    PriceListCreate,
    PriceListUpdate,
    PriceListItem,
    PriceListItemCreate,
    PriceListItemUpdate,
)
from app.services.price_list import PriceListService

router = APIRouter()


@router.get("/", response_model=List[PriceList])
def get_price_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Get all price lists (admin only)"""
    return PriceListService.get_price_lists(db, skip, limit)


@router.get("/{price_list_id}", response_model=PriceList)
def get_price_list(
    price_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Get a specific price list (admin only)"""
    return PriceListService.get_price_list(db, price_list_id)


@router.post("/", response_model=PriceList, status_code=201)
def create_price_list(
    price_list_in: PriceListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new price list (admin only)"""
    return PriceListService.create_price_list(db, price_list_in)


@router.put("/{price_list_id}", response_model=PriceList)
def update_price_list(
    price_list_id: int,
    price_list_update: PriceListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update a price list (admin only)"""
    return PriceListService.update_price_list(db, price_list_id, price_list_update)


@router.delete("/{price_list_id}", status_code=204)
def delete_price_list(
    price_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete a price list (admin only)"""
    PriceListService.delete_price_list(db, price_list_id)


@router.post("/{price_list_id}/users", response_model=PriceList)
def assign_users_to_price_list(
    price_list_id: int,
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Assign users to a price list (admin only)"""
    return PriceListService.assign_users_to_price_list(db, price_list_id, user_ids)


@router.delete("/{price_list_id}/users", response_model=PriceList)
def remove_users_from_price_list(
    price_list_id: int,
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Remove users from a price list (admin only)"""
    return PriceListService.remove_users_from_price_list(db, price_list_id, user_ids)


@router.post("/{price_list_id}/items", response_model=PriceListItem, status_code=201)
def add_product_to_price_list(
    price_list_id: int,
    item_in: PriceListItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Add a product with price to a price list (admin only)"""
    return PriceListService.add_product_to_price_list(db, price_list_id, item_in)


@router.put("/items/{item_id}", response_model=PriceListItem)
def update_price_list_item(
    item_id: int,
    item_update: PriceListItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update a price list item (admin only)"""
    return PriceListService.update_price_list_item(db, item_id, item_update)


@router.delete("/items/{item_id}", status_code=204)
def remove_product_from_price_list(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Remove a product from a price list (admin only)"""
    PriceListService.remove_product_from_price_list(db, item_id)
