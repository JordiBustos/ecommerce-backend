from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
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
    CSVImportResult,
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
    parent_only: bool = Query(
        default=False, description="Only return parent categories"
    ),
    db: Session = Depends(get_db),
):
    """Get all categories, optionally filter to parent categories only"""
    return CategoryService.get_categories(db, skip, limit, parent_only)


@router.get("/categories/{category_id}", response_model=CategoryWithSubcategories)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """Get category by ID with its subcategories"""
    return CategoryService.get_category(db, category_id)


@router.get(
    "/categories/{category_id}/subcategories", response_model=List[CategorySchema]
)
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


@router.delete("/all", status_code=200)
def delete_all_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete all products from database (admin only)"""
    count = ProductService.delete_all_products(db)
    return {"message": f"Successfully deleted {count} products"}


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """Delete product (admin only)"""
    ProductService.delete_product(db, product_id)
    return None


@router.post("/import/csv", response_model=CSVImportResult)
async def import_products_csv(
    file: UploadFile = File(...),
    batch_size: int = Query(
        50, ge=1, le=200, description="Number of products to process per batch"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Import products from CSV file (admin only).

    Processes products in batches of 50 (configurable).

    **Categories and Brands**: Use names instead of IDs. If a category or brand doesn't exist,
    it will be automatically created with other fields empty.

    Expected CSV format:
    ```
    name,price,category,slug,sku,ean,description,stock,is_always_in_stock,max_per_buy,weight,units_per_package,brand,image_url,is_active
    Product Name,19.99,Electronics,product-slug,SKU123,1234567890123,Description here,100,false,10,0.5,1,Logitech,https://example.com/image.jpg,true
    ```

    Required fields:
    - name: Product name
    - price: Product price (numeric)
    - category: Category name (will be created if doesn't exist)
    - slug: URL-friendly unique identifier

    Optional fields:
    - sku: Stock Keeping Unit (unique if provided)
    - ean: European Article Number (unique if provided)
    - description: Product description
    - stock: Stock quantity (default: 0)
    - is_always_in_stock: true/false (default: false)
    - max_per_buy: Maximum units per purchase (integer)
    - weight: Product weight (numeric)
    - units_per_package: Units per package (default: 1)
    - brand: Brand name (will be created if doesn't exist)
    - image_url: Product image URL
    - is_active: true/false (default: true)

    Returns:
    - total_rows: Total number of rows processed
    - successful: Number of successfully imported products
    - failed: Number of failed imports
    - errors: List of errors with row number and details
    - message: Summary message
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    return ProductService.import_products_from_csv(db, file.file, batch_size)
