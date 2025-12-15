from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.schemas.store import Store, StoreUpdate
from app.schemas.physical_store import PhysicalStore, PhysicalStoreCreate, PhysicalStoreUpdate
from app.services.store import StoreService
from app.services.physical_store import PhysicalStoreService

router = APIRouter()


@router.get("/", response_model=Store)
def get_store_settings(db: Session = Depends(get_db)):
    """Get store settings (public)"""
    return StoreService.get_store_settings(db)


@router.put("/", response_model=Store)
def update_store_settings(
    store_update: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update store settings (admin only)"""
    return StoreService.update_store_settings(db, store_update)


# Physical Stores Endpoints
@router.get("/physical-stores", response_model=List[PhysicalStore])
def get_physical_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True, description="Filter only active stores"),
    city: Optional[str] = Query(None, description="Filter by city name"),
    db: Session = Depends(get_db),
):
    """Get all physical stores (public)"""
    return PhysicalStoreService.get_stores(db, skip, limit, active_only, city)


@router.get("/physical-stores/{store_id}", response_model=PhysicalStore)
def get_physical_store(
    store_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific physical store (public)"""
    return PhysicalStoreService.get_store(db, store_id)


@router.post("/physical-stores", response_model=PhysicalStore)
def create_physical_store(
    store_in: PhysicalStoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new physical store (admin only)"""
    return PhysicalStoreService.create_store(db, store_in)


@router.put("/physical-stores/{store_id}", response_model=PhysicalStore)
def update_physical_store(
    store_id: int,
    store_update: PhysicalStoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update a physical store (admin only)"""
    return PhysicalStoreService.update_store(db, store_id, store_update)


@router.delete("/physical-stores/{store_id}")
def delete_physical_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete a physical store (admin only)"""
    PhysicalStoreService.delete_store(db, store_id)
    return {"message": "Physical store deleted successfully"}
