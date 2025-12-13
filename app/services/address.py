from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.address import Address
from app.models.user import User
from app.schemas.address import AddressCreate, AddressUpdate


class AddressService:
    @staticmethod
    def get_user_addresses(db: Session, user_id: int) -> List[Address]:
        """Get all addresses for a user"""
        return db.query(Address).filter(Address.user_id == user_id).all()

    @staticmethod
    def get_address(db: Session, address_id: int, user_id: int) -> Optional[Address]:
        """Get a specific address by ID for a user"""
        address = (
            db.query(Address)
            .filter(Address.id == address_id, Address.user_id == user_id)
            .first()
        )

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        return address

    @staticmethod
    def create_address(db: Session, user_id: int, address_in: AddressCreate) -> Address:
        """Create a new address for a user"""
        if address_in.is_default:
            db.query(Address).filter(Address.user_id == user_id).update(
                {"is_default": False}
            )

        address = Address(**address_in.model_dump(), user_id=user_id)
        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def update_address(
        db: Session, address_id: int, user_id: int, address_update: AddressUpdate
    ) -> Address:
        """Update an existing address"""
        address = AddressService.get_address(db, address_id, user_id)

        if address_update.is_default:
            db.query(Address).filter(Address.user_id == user_id).update(
                {"is_default": False}
            )

        update_data = address_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)

        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def delete_address(db: Session, address_id: int, user_id: int) -> None:
        """Delete an address"""
        address = AddressService.get_address(db, address_id, user_id)
        db.delete(address)
        db.commit()
