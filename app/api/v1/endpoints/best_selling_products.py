from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_superuser
from app.schemas.product import Product
from app.schemas.user import User
from app.services.best_selling import BestSellingService

router = APIRouter()


@router.get("/", response_model=List[Product])
def get_best_selling_products(
    limit: int = Query(default=12, ge=1, le=50, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Get the top best-selling products based on order history.
    
    **Performance:** This endpoint uses Redis caching with a 5-minute TTL to improve response times.
    The first request will query the database and cache the results. Subsequent requests within
    the cache window will be served from Redis.
    """
    return BestSellingService.get_best_selling_products(db, limit)


@router.post("/cache/clear", status_code=204)
def clear_best_selling_cache(
    current_user: User = Depends(get_current_superuser)
):
    """
    Clear the best-selling products cache (Admin only).
    
    Use this endpoint after updating products or orders to force cache refresh.
    """
    BestSellingService.clear_cache()
    return None
