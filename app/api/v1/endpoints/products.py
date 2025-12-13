from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_current_superuser
from app.db.base import get_db
from app.models.user import User
from app.schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate,
    CategoryWithSubcategories,
    Brand as BrandSchema,
    BrandCreate,
    BrandUpdate,
)
from app.services.product import CategoryService, ProductService, BrandService

router = APIRouter()


# Brands
@router.post("/brands", response_model=BrandSchema, status_code=201)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new brand (admin only)"""
    return BrandService.create_brand(db, brand_in)


@router.get("/brands", response_model=List[BrandSchema])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all brands"""
    return BrandService.get_brands(db, skip, limit)


@router.get("/brands/{brand_id}", response_model=BrandSchema)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get brand by ID"""
    return BrandService.get_brand(db, brand_id)


@router.put("/brands/{brand_id}", response_model=BrandSchema)
def update_brand(
    brand_id: int,
    brand_in: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update brand (admin only)"""
    return BrandService.update_brand(db, brand_id, brand_in)


@router.delete("/brands/{brand_id}", status_code=204)
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete brand (admin only)"""
    BrandService.delete_brand(db, brand_id)
    return None


# Categories
@router.post("/categories", response_model=CategorySchema, status_code=201)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new category or subcategory (admin only)"""
    return CategoryService.create_category(db, category_in)


@router.get("/categories", response_model=List[CategorySchema])
def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    parent_only: bool = Query(default=False, description="Only return parent categories"),
    db: Session = Depends(get_db)
):
    """Get all categories, optionally filter to parent categories only"""
    return CategoryService.get_categories(db, skip, limit, parent_only)


@router.get("/categories/{category_id}", response_model=CategoryWithSubcategories)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID with its subcategories"""
    return CategoryService.get_category(db, category_id)


@router.get("/categories/{category_id}/subcategories", response_model=List[CategorySchema])
def read_subcategories(category_id: int, db: Session = Depends(get_db)):
    """Get all subcategories of a category"""
    return CategoryService.get_subcategories(db, category_id)


@router.put("/categories/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update category (admin only)"""
    return CategoryService.update_category(db, category_id, category_in)


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete category (admin only)"""
    CategoryService.delete_category(db, category_id)
    return None


# Products
@router.post("/", response_model=ProductSchema, status_code=201)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Create a new product (admin only)"""
    return ProductService.create_product(db, product_in)


@router.get("/search/", response_model=List[ProductSchema])
def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search products across multiple fields (optimized).
    Searches in: name, description, SKU, EAN, category name, brand name.
    """
    return ProductService.search_products(db, q, skip, limit)


@router.get("/", response_model=List[ProductSchema])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all products with optional filters"""
    return ProductService.get_products(db, skip, limit, category_id, search)


@router.get("/{product_id}", response_model=ProductSchema)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    return ProductService.get_product(db, product_id)


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Update product (admin only)"""
    return ProductService.update_product(db, product_id, product_in)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete product (admin only)"""
    ProductService.delete_product(db, product_id)
    return None
