from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.product import Product
from app.services.best_selling import BestSellingService

router = APIRouter()


@router.get("/", response_model=List[Product])
def get_best_selling_products(
    limit: int = Query(default=12, ge=1, le=50, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """Get the top best-selling products based on order history"""
    return BestSellingService.get_best_selling_products(db, limit)
