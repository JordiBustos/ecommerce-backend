from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.address import Address, AddressCreate, AddressUpdate
from app.services.address import AddressService

router = APIRouter()


@router.get("/", response_model=List[Address])
def get_user_addresses(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all addresses for the current user"""
    return AddressService.get_user_addresses(db, current_user.id)


@router.get("/{address_id}", response_model=Address)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific address"""
    return AddressService.get_address(db, address_id, current_user.id)


@router.post("/", response_model=Address, status_code=201)
def create_address(
    address_in: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new address"""
    return AddressService.create_address(db, current_user.id, address_in)


@router.put("/{address_id}", response_model=Address)
def update_address(
    address_id: int,
    address_update: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing address"""
    return AddressService.update_address(
        db, address_id, current_user.id, address_update
    )


@router.delete("/{address_id}", status_code=204)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an address"""
    AddressService.delete_address(db, address_id, current_user.id)
