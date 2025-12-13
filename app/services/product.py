from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException
from app.models.product import Product, Category, Brand
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    CategoryCreate,
    CategoryUpdate,
    BrandCreate,
    BrandUpdate,
)


class BrandService:
    @staticmethod
    def create_brand(db: Session, brand_in: BrandCreate) -> Brand:
        """Create a new brand"""
        existing = db.query(Brand).filter(Brand.slug == brand_in.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Brand with this slug already exists")
        
        brand = Brand(**brand_in.model_dump())
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def get_brands(db: Session, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Get all brands with pagination"""
        return db.query(Brand).offset(skip).limit(limit).all()

    @staticmethod
    def get_brand(db: Session, brand_id: int) -> Brand:
        """Get brand by ID"""
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    @staticmethod
    def update_brand(db: Session, brand_id: int, brand_in: BrandUpdate) -> Brand:
        """Update brand"""
        brand = BrandService.get_brand(db, brand_id)
        update_data = brand_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)
        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def delete_brand(db: Session, brand_id: int) -> None:
        """Delete brand"""
        brand = BrandService.get_brand(db, brand_id)
        db.delete(brand)
        db.commit()


class CategoryService:
    @staticmethod
    def create_category(db: Session, category_in: CategoryCreate) -> Category:
        """Create a new category or subcategory"""
        existing = db.query(Category).filter(Category.slug == category_in.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this slug already exists")
        
        if category_in.parent_id:
            parent = db.query(Category).filter(Category.id == category_in.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")
        
        category = Category(**category_in.model_dump())
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100, parent_only: bool = False) -> List[Category]:
        """Get all categories with pagination"""
        query = db.query(Category)
        if parent_only:
            query = query.filter(Category.parent_id == None)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_category(db: Session, category_id: int) -> Category:
        """Get category by ID"""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    
    @staticmethod
    def get_subcategories(db: Session, category_id: int) -> List[Category]:
        """Get all subcategories of a category"""
        return db.query(Category).filter(Category.parent_id == category_id).all()

    @staticmethod
    def update_category(
        db: Session, category_id: int, category_in: CategoryUpdate
    ) -> Category:
        """Update category"""
        category = CategoryService.get_category(db, category_id)
        update_data = category_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> None:
        """Delete category"""
        category = CategoryService.get_category(db, category_id)
        db.delete(category)
        db.commit()


class ProductService:
    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        """Create a new product"""
        category = (
            db.query(Category).filter(Category.id == product_in.category_id).first()
        )
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        product = Product(**product_in.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Product]:
        """Get all products with pagination and filters"""
        query = db.query(Product).filter(Product.is_active == True)

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_product(db: Session, product_id: int) -> Product:
        """Get product by ID"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    @staticmethod
    def update_product(
        db: Session, product_id: int, product_in: ProductUpdate
    ) -> Product:
        """Update product"""
        product = ProductService.get_product(db, product_id)
        update_data = product_in.model_dump(exclude_unset=True)

        if "category_id" in update_data:
            category = (
                db.query(Category)
                .filter(Category.id == update_data["category_id"])
                .first()
            )
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

        for field, value in update_data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> None:
        """Delete product"""
        product = ProductService.get_product(db, product_id)
        db.delete(product)
        db.commit()

    @staticmethod
    def search_products(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """
        Search products across multiple fields optimized with joins.
        Searches in: product name, description, SKU, EAN, category name, brand name
        """
        search_term = f"%{query}%"
        
        # Build query with eager loading to avoid N+1 queries
        products_query = (
            db.query(Product)
            .outerjoin(Category, Product.category_id == Category.id)
            .outerjoin(Brand, Product.brand_id == Brand.id)
            .filter(Product.is_active == True)
            .filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.ean.ilike(search_term),
                    Category.name.ilike(search_term),
                    Brand.name.ilike(search_term),
                )
            )
            .options(joinedload(Product.category), joinedload(Product.brand))
            .distinct()
        )
        
        return products_query.offset(skip).limit(limit).all()
