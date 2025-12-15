"""
Price Calculation Service
Implements Strategy pattern for different pricing strategies.
Centralizes all price calculation logic to follow DRY principles.
"""

from typing import Optional, Protocol, List
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.user import User
from app.models.price_list import PriceList, PriceListItem
from decimal import Decimal


class PricingStrategy(Protocol):
    """Protocol for pricing strategies"""
    
    def calculate_price(self, product: Product, user: Optional[User], db: Session) -> float:
        """Calculate price based on strategy rules"""
        ...


class BasePricingStrategy:
    """Default pricing strategy using product base price"""
    
    @staticmethod
    def calculate_price(product: Product, user: Optional[User], db: Session) -> float:
        """Return product's base price"""
        return product.price


class PriceListPricingStrategy:
    """Pricing strategy that checks user's assigned price list"""
    
    @staticmethod
    def calculate_price(product: Product, user: Optional[User], db: Session) -> float:
        """
        Return custom price from user's price list if exists,
        otherwise return base price
        """
        if not user:
            return product.price
        
        # Check if user has assigned price list
        price_list = (
            db.query(PriceList)
            .join(PriceList.users)
            .filter(User.id == user.id, PriceList.is_active == True)
            .first()
        )
        
        if not price_list:
            return product.price
        
        # Check if product has custom price in this price list
        price_list_item = (
            db.query(PriceListItem)
            .filter(
                PriceListItem.price_list_id == price_list.id,
                PriceListItem.product_id == product.id
            )
            .first()
        )
        
        return price_list_item.price if price_list_item else product.price


class PriceCalculator:
    """
    Centralized price calculation service using Strategy pattern.
    Provides reusable pricing logic for products across the application.
    """
    
    @staticmethod
    def get_product_price(
        product: Product,
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> float:
        """
        Get the applicable price for a product based on user and context.
        Uses Strategy pattern to determine pricing.
        
        Args:
            product: Product to get price for
            user: Optional user (for price list pricing)
            db: Optional database session (required for price list pricing)
        
        Returns:
            float: Calculated price
        """
        if user and db:
            strategy = PriceListPricingStrategy()
            return strategy.calculate_price(product, user, db)
        else:
            strategy = BasePricingStrategy()
            return strategy.calculate_price(product, user, db)
    
    @staticmethod
    def calculate_item_total(
        product: Product,
        quantity: int,
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> float:
        """
        Calculate total price for a quantity of products.
        
        Args:
            product: Product to calculate price for
            quantity: Quantity of products
            user: Optional user (for price list pricing)
            db: Optional database session (required for price list pricing)
        
        Returns:
            float: Total price (price * quantity)
        """
        price = PriceCalculator.get_product_price(product, user, db)
        return round(price * quantity, 2)
    
    @staticmethod
    def calculate_cart_total(
        items: List[tuple[Product, int]],
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> float:
        """
        Calculate total price for multiple items (entire cart).
        
        Args:
            items: List of (product, quantity) tuples
            user: Optional user (for price list pricing)
            db: Optional database session (required for price list pricing)
        
        Returns:
            float: Total cart price
        """
        total = 0.0
        for product, quantity in items:
            total += PriceCalculator.calculate_item_total(product, quantity, user, db)
        return round(total, 2)
    
    @staticmethod
    def get_price_with_discount(
        product: Product,
        discount_percent: float,
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> float:
        """
        Calculate discounted price for a product.
        
        Args:
            product: Product to calculate price for
            discount_percent: Discount percentage (0-100)
            user: Optional user (for base price calculation)
            db: Optional database session
        
        Returns:
            float: Discounted price
        """
        base_price = PriceCalculator.get_product_price(product, user, db)
        discount_multiplier = 1 - (discount_percent / 100)
        return round(base_price * discount_multiplier, 2)
    
    @staticmethod
    def compare_prices(
        product: Product,
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> dict:
        """
        Get both base price and user-specific price for comparison.
        Useful for displaying savings.
        
        Args:
            product: Product to compare prices for
            user: Optional user (for price list pricing)
            db: Optional database session
        
        Returns:
            dict: Dictionary with 'base_price', 'user_price', and 'savings'
        """
        base_price = product.price
        user_price = PriceCalculator.get_product_price(product, user, db) if user and db else base_price
        savings = base_price - user_price if user_price < base_price else 0.0
        
        return {
            "base_price": round(base_price, 2),
            "user_price": round(user_price, 2),
            "savings": round(savings, 2),
            "savings_percent": round((savings / base_price * 100), 2) if base_price > 0 else 0.0
        }
