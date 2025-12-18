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
    """Pricing strategy that checks user's role and assigned price list"""
    
    @staticmethod
    def calculate_price(product: Product, user: Optional[User], db: Session) -> float:
        """
        Calculate price based on user's role and price list.
        Priority:
        1. Price list price (if user has role with price list)
        2. Offer price (if set and lower than current price)
        3. Base product price
        
        Args:
            product: Product to calculate price for
            user: Optional user (for role-based pricing)
            db: Database session
        """
        if not user or not db:
            return product.price
        
        user_roles = user.roles if hasattr(user, 'roles') else []
        applicable_price = product.price
        
        for role in user_roles:
            price_list = (
                db.query(PriceList)
                .filter(
                    PriceList.role_filter == role.slug,
                    PriceList.is_active == True
                )
                .first()
            )
            
            if price_list:
                price_list_item = (
                    db.query(PriceListItem)
                    .filter(
                        PriceListItem.price_list_id == price_list.id,
                        PriceListItem.product_id == product.id
                    )
                    .first()
                )
                
                if price_list_item:
                    # Use price list price directly - price lists override base price
                    applicable_price = price_list_item.price
                    break
        
        # Apply offer price if it's lower than current applicable price
        if product.offer_price and product.offer_price > 0:
            applicable_price = min(applicable_price, product.offer_price)
        
        return applicable_price


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
        Useful for displaying savings in product cards.
        
        Args:
            product: Product to compare prices for
            user: Optional user (for price list pricing)
            db: Optional database session
        
        Returns:
            dict: Dictionary with pricing information
            {
                'base_price': float,          # Original product price
                'final_price': float,         # Price user will pay
                'has_discount': bool,         # True if user gets a discount
                'savings': float,             # Amount saved
                'savings_percent': float,     # Percentage saved
                'discount_source': str|None   # 'offer', 'role_price_list', or None
            }
        """
        base_price = product.price
        final_price = PriceCalculator.get_product_price(product, user, db) if user and db else base_price
        savings = base_price - final_price if final_price < base_price else 0.0
        has_discount = savings > 0
        
        # Determine discount source
        discount_source = None
        if has_discount:
            if product.offer_price and product.offer_price > 0 and final_price == product.offer_price:
                discount_source = 'offer'
            elif final_price < base_price:
                discount_source = 'role_price_list'
        
        return {
            "base_price": round(base_price, 2),
            "final_price": round(final_price, 2),
            "has_discount": has_discount,
            "savings": round(savings, 2),
            "savings_percent": round((savings / base_price * 100), 2) if base_price > 0 else 0.0,
            "discount_source": discount_source
        }
