from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.physical_store import PhysicalStore
from app.schemas.physical_store import PhysicalStoreCreate, PhysicalStoreUpdate


class PhysicalStoreService:
    @staticmethod
    def create_store(db: Session, store_in: PhysicalStoreCreate) -> PhysicalStore:
        """Create a new physical store"""
        db_store = PhysicalStore(**store_in.model_dump())
        db.add(db_store)
        db.commit()
        db.refresh(db_store)
        return db_store

    @staticmethod
    def get_store(db: Session, store_id: int) -> PhysicalStore:
        """Get a physical store by ID"""
        store = db.query(PhysicalStore).filter(PhysicalStore.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return store

    @staticmethod
    def get_stores(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        active_only: bool = True,
        city: Optional[str] = None
    ) -> List[PhysicalStore]:
        """Get all physical stores with optional filters"""
        query = db.query(PhysicalStore)
        
        if active_only:
            query = query.filter(PhysicalStore.is_active == True)
        
        if city:
            query = query.filter(PhysicalStore.city.ilike(f"%{city}%"))
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_store(
        db: Session, store_id: int, store_update: PhysicalStoreUpdate
    ) -> PhysicalStore:
        """Update a physical store"""
        db_store = db.query(PhysicalStore).filter(PhysicalStore.id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")

        update_data = store_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_store, field, value)

        db.commit()
        db.refresh(db_store)
        return db_store

    @staticmethod
    def delete_store(db: Session, store_id: int) -> None:
        """Delete a physical store"""
        db_store = db.query(PhysicalStore).filter(PhysicalStore.id == store_id).first()
        if not db_store:
            raise HTTPException(status_code=404, detail="Store not found")

        db.delete(db_store)
        db.commit()
