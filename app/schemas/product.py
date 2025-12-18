from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    logo_url: Optional[str] = None


class Brand(BrandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    image_url: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryWithSubcategories(Category):
    subcategories: List["Category"] = []
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: Optional[str] = None
    ean: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: float
    offer_price: Optional[float] = None
    stock: int = 0
    is_always_in_stock: bool = False
    max_per_buy: Optional[int] = None
    weight: Optional[float] = None
    units_per_package: int = 1
    category_id: int
    brand_id: Optional[int] = None
    image_url: Optional[str] = None
    slug: str


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    ean: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    offer_price: Optional[float] = None
    stock: Optional[int] = None
    is_always_in_stock: Optional[bool] = None
    max_per_buy: Optional[int] = None
    weight: Optional[float] = None
    units_per_package: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    image_url: Optional[str] = None
    slug: Optional[str] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    
    # Optional pricing information (calculated fields, not from DB)
    final_price: Optional[float] = None
    has_discount: Optional[bool] = None
    savings: Optional[float] = None
    savings_percent: Optional[float] = None
    discount_source: Optional[str] = None

    class Config:
        from_attributes = True


class CSVImportError(BaseModel):
    row: int
    data: Dict[str, Any]
    error: str


class CSVImportResult(BaseModel):
    total_rows: int
    successful: int
    failed: int
    errors: List[CSVImportError] = []
    message: str


class ProductListResponse(BaseModel):
    products: List[Product]
    total: int


class ProductPricingInfo(BaseModel):
    """Pricing information for a product including discounts"""
    base_price: float
    final_price: float
    has_discount: bool
    savings: float
    savings_percent: float
    discount_source: Optional[str] = None  # 'offer', 'role_price_list', or None
