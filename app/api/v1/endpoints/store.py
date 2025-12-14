from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.schemas.store import Store, StoreUpdate
from app.services.store import StoreService

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
