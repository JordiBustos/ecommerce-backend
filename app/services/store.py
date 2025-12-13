from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate


class StoreService:
    @staticmethod
    def get_store_settings(db: Session) -> Store:
        """Get store settings (always returns the first/only record)"""
        store = db.query(Store).first()
        if not store:
            # Create default settings if none exist
            store = Store(
                store_name="My E-Commerce Store",
                primary_color="#3B82F6",
                secondary_color="#10B981",
                accent_color="#F59E0B",
                currency="EUR",
                tax_rate=0.21,
                opening_hours={
                    "monday": {"open": "09:00", "close": "18:00", "closed": False},
                    "tuesday": {"open": "09:00", "close": "18:00", "closed": False},
                    "wednesday": {"open": "09:00", "close": "18:00", "closed": False},
                    "thursday": {"open": "09:00", "close": "18:00", "closed": False},
                    "friday": {"open": "09:00", "close": "18:00", "closed": False},
                    "saturday": {"open": "10:00", "close": "14:00", "closed": False},
                    "sunday": {"closed": True}
                }
            )
            db.add(store)
            db.commit()
            db.refresh(store)
        return store
    
    @staticmethod
    def update_store_settings(db: Session, store_update: StoreUpdate) -> Store:
        """Update store settings"""
        store = StoreService.get_store_settings(db)
        
        update_data = store_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(store, field, value)
        
        db.commit()
        db.refresh(store)
        return store
