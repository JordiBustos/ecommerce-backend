from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import Cart, CartItemCreate, CartItemUpdate
from app.services.product_validator import ProductValidator
from app.services.price_calculator import PriceCalculator


class CartService:
    @staticmethod
    def get_user_cart(db: Session, user: User) -> Cart:
        """
        Get user's shopping cart with calculated prices.
        Uses PriceCalculator to apply user-specific pricing.
        """
        cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
        
        # Calculate total using PriceCalculator for user-specific pricing
        items_for_calc = [(item.product, item.quantity) for item in cart_items]
        total = PriceCalculator.calculate_cart_total(items_for_calc, user, db)
        
        return Cart(items=cart_items, total=total)

    @staticmethod
    def add_item_to_cart(db: Session, user: User, item_in: CartItemCreate) -> Cart:
        """
        Add item to cart or update quantity if already exists.
        Uses ProductValidator for validation (Strategy pattern).
        """
        # Validate product and quantity using ProductValidator
        product = ProductValidator.validate_product_and_quantity(
            db, item_in.product_id, item_in.quantity, context="cart"
        )

        existing_item = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user.id, CartItem.product_id == item_in.product_id
            )
            .first()
        )

        if existing_item:
            # Validate that adding this quantity won't exceed limits
            ProductValidator.validate_can_add_quantity(
                product, existing_item.quantity, item_in.quantity
            )
            existing_item.quantity += item_in.quantity
        else:
            cart_item = CartItem(
                user_id=user.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity,
            )
            db.add(cart_item)

        db.commit()

        return CartService.get_user_cart(db, user)

    @staticmethod
    def update_cart_item(
        db: Session, user: User, item_id: int, item_update: CartItemUpdate
    ) -> Cart:
        """
        Update cart item quantity.
        Uses ProductValidator for validation.
        """
        cart_item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.user_id == user.id)
            .first()
        )

        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        # Validate new quantity using ProductValidator
        ProductValidator.validate_for_cart(cart_item.product, item_update.quantity)

        cart_item.quantity = item_update.quantity
        db.commit()

        return CartService.get_user_cart(db, user)

    @staticmethod
    def remove_item_from_cart(db: Session, user: User, item_id: int) -> None:
        """Remove item from cart"""
        cart_item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.user_id == user.id)
            .first()
        )

        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        db.delete(cart_item)
        db.commit()

    @staticmethod
    def clear_cart(db: Session, user: User) -> None:
        """Clear all items from user's cart"""
        db.query(CartItem).filter(CartItem.user_id == user.id).delete()
        db.commit()
