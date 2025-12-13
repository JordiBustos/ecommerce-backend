from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.product import Product
from app.models.order import OrderItem


class BestSellingService:
    @staticmethod
    def get_best_selling_products(db: Session, limit: int = 12) -> List[Product]:
        """Get the top N best-selling products based on order history"""
        best_sellers = (
            db.query(
                Product,
                func.sum(OrderItem.quantity).label('total_sold')
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id)
            .order_by(desc('total_sold'))
            .limit(limit)
            .all()
        )
        
        return [product for product, _ in best_sellers]
