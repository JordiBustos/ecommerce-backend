from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.price_list import PriceList, PriceListItem
from app.models.user import User
from app.models.product import Product
from app.schemas.price_list import (
    PriceListCreate,
    PriceListUpdate,
    PriceListItemCreate,
    PriceListItemUpdate,
)


class PriceListService:
    @staticmethod
    def get_price_lists(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[PriceList]:
        """Get all price lists"""
        return db.query(PriceList).offset(skip).limit(limit).all()

    @staticmethod
    def get_price_list(db: Session, price_list_id: int) -> PriceList:
        """Get a specific price list by ID"""
        price_list = db.query(PriceList).filter(PriceList.id == price_list_id).first()
        if not price_list:
            raise HTTPException(status_code=404, detail="Price list not found")
        return price_list

    @staticmethod
    def create_price_list(db: Session, price_list_in: PriceListCreate) -> PriceList:
        """Create a new price list"""
        existing = (
            db.query(PriceList).filter(PriceList.name == price_list_in.name).first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Price list with this name already exists"
            )

        price_list = PriceList(**price_list_in.model_dump())
        db.add(price_list)
        db.commit()
        db.refresh(price_list)
        return price_list

    @staticmethod
    def update_price_list(
        db: Session, price_list_id: int, price_list_update: PriceListUpdate
    ) -> PriceList:
        """Update an existing price list"""
        price_list = PriceListService.get_price_list(db, price_list_id)

        update_data = price_list_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(price_list, field, value)

        db.commit()
        db.refresh(price_list)
        return price_list

    @staticmethod
    def delete_price_list(db: Session, price_list_id: int) -> None:
        """Delete a price list"""
        price_list = PriceListService.get_price_list(db, price_list_id)
        db.delete(price_list)
        db.commit()

    @staticmethod
    def assign_users_to_price_list(
        db: Session, price_list_id: int, user_ids: List[int]
    ) -> PriceList:
        """Assign users to a price list"""
        price_list = PriceListService.get_price_list(db, price_list_id)

        users = db.query(User).filter(User.id.in_(user_ids)).all()
        if len(users) != len(user_ids):
            raise HTTPException(status_code=404, detail="One or more users not found")

        price_list.users = users
        db.commit()
        db.refresh(price_list)
        return price_list

    @staticmethod
    def remove_users_from_price_list(
        db: Session, price_list_id: int, user_ids: List[int]
    ) -> PriceList:
        """Remove users from a price list"""
        price_list = PriceListService.get_price_list(db, price_list_id)

        price_list.users = [
            user for user in price_list.users if user.id not in user_ids
        ]
        db.commit()
        db.refresh(price_list)
        return price_list

    @staticmethod
    def add_product_to_price_list(
        db: Session, price_list_id: int, item_in: PriceListItemCreate
    ) -> PriceListItem:
        """Add a product with price to a price list"""
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        existing_item = (
            db.query(PriceListItem)
            .filter(
                PriceListItem.price_list_id == price_list_id,
                PriceListItem.product_id == item_in.product_id,
            )
            .first()
        )

        if existing_item:
            raise HTTPException(
                status_code=400, detail="Product already exists in this price list"
            )

        item = PriceListItem(
            price_list_id=price_list_id,
            product_id=item_in.product_id,
            price=item_in.price,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def update_price_list_item(
        db: Session, item_id: int, item_update: PriceListItemUpdate
    ) -> PriceListItem:
        """Update a price list item"""
        item = db.query(PriceListItem).filter(PriceListItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Price list item not found")

        if item_update.price is not None:
            item.price = item_update.price

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def remove_product_from_price_list(db: Session, item_id: int) -> None:
        """Remove a product from a price list"""
        item = db.query(PriceListItem).filter(PriceListItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Price list item not found")

        db.delete(item)
        db.commit()

    @staticmethod
    def get_user_price_list(db: Session, user_id: int) -> Optional[PriceList]:
        """Get the applicable price list for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        for price_list in user.price_lists:
            if price_list.is_active:
                return price_list

        return None
