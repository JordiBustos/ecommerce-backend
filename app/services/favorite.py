from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.product import Product
from app.models.favorite import user_favorites


class FavoriteService:
    @staticmethod
    def add_favorite(db: Session, user_id: int, product_id: int) -> dict:
        """Add a product to user's favorites"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if product in user.favorite_products:
            raise HTTPException(status_code=400, detail="Product already in favorites")

        user.favorite_products.append(product)
        db.commit()
        return {"message": "Product added to favorites"}

    @staticmethod
    def remove_favorite(db: Session, user_id: int, product_id: int) -> dict:
        """Remove a product from user's favorites"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product not in user.favorite_products:
            raise HTTPException(status_code=404, detail="Product not in favorites")

        user.favorite_products.remove(product)
        db.commit()
        return {"message": "Product removed from favorites"}

    @staticmethod
    def get_user_favorites(db: Session, user_id: int) -> List[Product]:
        """Get all favorite products for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user.favorite_products
