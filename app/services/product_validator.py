"""
Product Validation Service
Implements Strategy and Chain of Responsibility patterns for product validation.
This service centralizes all product-related validations to follow DRY principles.
"""

from typing import Protocol
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.product import Product


class ValidationStrategy(Protocol):
    """Protocol for validation strategies"""

    def validate(self, product: Product, quantity: int) -> None:
        """Validate product based on strategy rules"""
        ...


class StockValidationStrategy:
    """Strategy for validating stock availability"""

    @staticmethod
    def validate(product: Product, quantity: int) -> None:
        """Check if product has sufficient stock"""
        if not product.is_always_in_stock and product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name}. Available: {product.stock}, Requested: {quantity}",
            )


class PurchaseLimitValidationStrategy:
    """Strategy for validating purchase limits"""

    @staticmethod
    def validate(product: Product, quantity: int) -> None:
        """Check if quantity exceeds purchase limit"""
        if product.max_per_buy and quantity > product.max_per_buy:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot purchase more than {product.max_per_buy} units of {product.name}",
            )


class ProductActiveValidationStrategy:
    """Strategy for validating product is active"""

    @staticmethod
    def validate(product: Product, quantity: int) -> None:
        """Check if product is active"""
        if not product.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Product {product.name} is not available for purchase",
            )


class ValidationChain:
    """
    Chain of Responsibility pattern for running multiple validations.
    Each validation strategy is executed in sequence.
    """

    def __init__(self):
        self.strategies: list[ValidationStrategy] = []

    def add_strategy(self, strategy: ValidationStrategy) -> "ValidationChain":
        """Add a validation strategy to the chain"""
        self.strategies.append(strategy)
        return self

    def validate(self, product: Product, quantity: int) -> None:
        """Execute all validation strategies in the chain"""
        for strategy in self.strategies:
            strategy.validate(product, quantity)


class ProductValidator:
    """
    Centralized product validation service using Strategy pattern.
    Provides reusable validation logic for products across the application.
    """

    @staticmethod
    def get_product_or_404(db: Session, product_id: int) -> Product:
        """
        Repository pattern: Get product by ID or raise 404.
        Centralizes product retrieval logic.
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    @staticmethod
    def validate_stock(product: Product, quantity: int) -> None:
        """Validate product stock availability"""
        StockValidationStrategy.validate(product, quantity)

    @staticmethod
    def validate_purchase_limit(product: Product, quantity: int) -> None:
        """Validate purchase quantity limits"""
        PurchaseLimitValidationStrategy.validate(product, quantity)

    @staticmethod
    def validate_product_active(product: Product, quantity: int = 0) -> None:
        """Validate product is active"""
        ProductActiveValidationStrategy.validate(product, quantity)

    @staticmethod
    def validate_for_cart(product: Product, quantity: int) -> None:
        """
        Complete validation for adding to cart.
        Uses Chain of Responsibility pattern.
        """
        chain = ValidationChain()
        chain.add_strategy(ProductActiveValidationStrategy()).add_strategy(
            StockValidationStrategy()
        ).add_strategy(PurchaseLimitValidationStrategy()).validate(product, quantity)

    @staticmethod
    def validate_for_order(product: Product, quantity: int) -> None:
        """
        Complete validation for order creation.
        Uses Chain of Responsibility pattern.
        """
        chain = ValidationChain()
        chain.add_strategy(ProductActiveValidationStrategy()).add_strategy(
            StockValidationStrategy()
        ).add_strategy(PurchaseLimitValidationStrategy()).validate(product, quantity)

    @staticmethod
    def validate_product_and_quantity(
        db: Session, product_id: int, quantity: int, context: str = "cart"
    ) -> Product:
        """
        Facade pattern: Simplifies validation by combining retrieval and validation.

        Args:
            db: Database session
            product_id: ID of the product to validate
            quantity: Quantity to validate
            context: Context for validation ('cart' or 'order')

        Returns:
            Product: Validated product
        """
        product = ProductValidator.get_product_or_404(db, product_id)

        if context == "cart":
            ProductValidator.validate_for_cart(product, quantity)
        elif context == "order":
            ProductValidator.validate_for_order(product, quantity)
        else:
            # Default validation
            ProductValidator.validate_stock(product, quantity)
            ProductValidator.validate_purchase_limit(product, quantity)

        return product

    @staticmethod
    def can_add_quantity(
        product: Product, current_quantity: int, additional_quantity: int
    ) -> bool:
        """
        Check if additional quantity can be added to existing quantity.
        Useful for cart updates.
        """
        new_total = current_quantity + additional_quantity

        try:
            ProductValidator.validate_stock(product, new_total)
            ProductValidator.validate_purchase_limit(product, new_total)
            return True
        except HTTPException:
            return False

    @staticmethod
    def validate_can_add_quantity(
        product: Product, current_quantity: int, additional_quantity: int
    ) -> None:
        """
        Validate that additional quantity can be added.
        Raises HTTPException if validation fails.
        """
        new_total = current_quantity + additional_quantity
        ProductValidator.validate_stock(product, new_total)
        ProductValidator.validate_purchase_limit(product, new_total)
