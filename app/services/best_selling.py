from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import redis
import json
import logging
from app.models.product import Product
from app.models.order import OrderItem
from app.models.user import User
from app.core.config import settings
from app.services.price_calculator import PriceCalculator

logger = logging.getLogger(__name__)


class BestSellingService:
    _redis_client: Optional[redis.Redis] = None

    @classmethod
    def get_redis_client(cls) -> Optional[redis.Redis]:
        """Get or create Redis client. Returns None if Redis is not available."""
        if cls._redis_client is None:
            try:
                cls._redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=(
                        settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None
                    ),
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                cls._redis_client.ping()
                logger.info("Redis connection established")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(
                    f"Redis not available: {e}. Falling back to database-only queries."
                )
                cls._redis_client = None
        return cls._redis_client

    @staticmethod
    def get_cache_key(limit: int) -> str:
        """Generate cache key for best-selling products"""
        return f"best_selling:limit:{limit}"

    @classmethod
    def get_best_selling_products(cls, db: Session, limit: int = 12, user: Optional[User] = None) -> List[Product]:
        """
        Get the top N best-selling products based on order history.
        Uses Redis cache with TTL to improve performance.
        Calculates pricing based on user's roles and price lists.
        
        Args:
            db: Database session
            limit: Number of products to return
            user: Optional user for calculating personalized pricing
        
        Returns:
            List of products with pricing information
        """
        cache_key = cls.get_cache_key(limit)
        redis_client = cls.get_redis_client()

        if redis_client:
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"Cache HIT for {cache_key}")
                    product_ids = json.loads(cached_data)
                    products = (
                        db.query(Product).filter(Product.id.in_(product_ids)).all()
                    )
                    product_dict = {p.id: p for p in products}
                    ordered_products = [
                        product_dict[pid] for pid in product_ids if pid in product_dict
                    ]
                    
                    # Add pricing information to each product
                    for product in ordered_products:
                        pricing_info = PriceCalculator.compare_prices(product, user, db)
                        product.final_price = pricing_info["final_price"]
                        product.has_discount = pricing_info["has_discount"]
                        product.savings = pricing_info["savings"]
                        product.savings_percent = pricing_info["savings_percent"]
                        product.discount_source = pricing_info["discount_source"]
                    
                    return ordered_products
            except Exception as e:
                logger.error(f"Redis cache read error: {e}")

        logger.info(f"Cache MISS for {cache_key} - querying database")
        best_sellers = (
            db.query(Product, func.sum(OrderItem.quantity).label("total_sold"))
            .join(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id)
            .order_by(desc("total_sold"))
            .limit(limit)
            .all()
        )

        products = [product for product, _ in best_sellers]

        # Add pricing information to each product
        for product in products:
            pricing_info = PriceCalculator.compare_prices(product, user, db)
            product.final_price = pricing_info["final_price"]
            product.has_discount = pricing_info["has_discount"]
            product.savings = pricing_info["savings"]
            product.savings_percent = pricing_info["savings_percent"]
            product.discount_source = pricing_info["discount_source"]

        if redis_client and products:
            try:
                product_ids = [p.id for p in products]
                redis_client.setex(
                    cache_key, settings.CACHE_TTL, json.dumps(product_ids)
                )
                logger.info(
                    f"Cached {len(product_ids)} product IDs with TTL {settings.CACHE_TTL}s"
                )
            except Exception as e:
                logger.error(f"Redis cache write error: {e}")

        return products

    @classmethod
    def clear_cache(cls) -> bool:
        """Clear all best-selling products cache. Returns True if successful."""
        redis_client = cls.get_redis_client()
        if redis_client:
            try:
                keys = redis_client.keys("best_selling:*")
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cache entries")
                return True
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                return False
        return False
