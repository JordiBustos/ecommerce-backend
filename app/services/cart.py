from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import Cart, CartItemCreate, CartItemUpdate


class CartService:
    @staticmethod
    def get_user_cart(db: Session, user: User) -> Cart:
        """Get user's shopping cart"""
        cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
        total = sum(item.product.price * item.quantity for item in cart_items)
        return Cart(items=cart_items, total=total)

    @staticmethod
    def add_item_to_cart(db: Session, user: User, item_in: CartItemCreate) -> Cart:
        """Add item to cart or update quantity if already exists"""
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item_in.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        existing_item = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == user.id, CartItem.product_id == item_in.product_id
            )
            .first()
        )

        if existing_item:
            new_quantity = existing_item.quantity + item_in.quantity
            if product.stock < new_quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            existing_item.quantity = new_quantity
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
        """Update cart item quantity"""
        cart_item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.user_id == user.id)
            .first()
        )

        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        if cart_item.product.stock < item_update.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

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
