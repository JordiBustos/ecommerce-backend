from typing import Optional, List, Dict, Any, BinaryIO
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException
import csv
import io
from app.models.product import Product, Category, Brand
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    CategoryCreate,
    CategoryUpdate,
    BrandCreate,
    BrandUpdate,
    CSVImportResult,
    CSVImportError,
)
from app.services.base import SlugUniqueService


class BrandService(SlugUniqueService[Brand, BrandCreate, BrandUpdate]):
    """
    Brand service with CRUD operations.
    Inherits common operations from SlugUniqueService (Repository pattern).
    """

    def __init__(self):
        super().__init__(Brand)

    def get_brands(self, db: Session, skip: int = 0, limit: int = 100) -> List[Brand]:
        """Get all brands with pagination"""
        return self.get_multi(db, skip, limit)

    def get_brand(self, db: Session, brand_id: int) -> Brand:
        """Get brand by ID"""
        return self.get(db, brand_id)

    def create_brand(self, db: Session, brand_in: BrandCreate) -> Brand:
        """Create a new brand"""
        return self.create(db, brand_in)

    def update_brand(self, db: Session, brand_id: int, brand_in: BrandUpdate) -> Brand:
        """Update brand"""
        return self.update(db, brand_id, brand_in)

    def delete_brand(self, db: Session, brand_id: int) -> None:
        """Delete brand"""
        self.delete(db, brand_id)


class CategoryService(SlugUniqueService[Category, CategoryCreate, CategoryUpdate]):
    """
    Category service with CRUD operations and hierarchy support.
    Inherits common operations from SlugUniqueService (Repository pattern).
    """

    def __init__(self):
        super().__init__(Category)

    def create_category(self, db: Session, category_in: CategoryCreate) -> Category:
        """Create a new category or subcategory with parent validation"""
        if category_in.parent_id:
            parent = (
                db.query(Category).filter(Category.id == category_in.parent_id).first()
            )
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")

        return self.create(db, category_in)

    def get_categories(
        self, db: Session, skip: int = 0, limit: int = 100, parent_only: bool = False
    ) -> List[Category]:
        """Get all categories with pagination"""
        if parent_only:
            query = db.query(Category).filter(Category.parent_id == None)
            return query.offset(skip).limit(limit).all()
        return self.get_multi(db, skip, limit)

    def get_category(self, db: Session, category_id: int) -> Category:
        """Get category by ID"""
        return self.get(db, category_id)

    def get_subcategories(self, db: Session, category_id: int) -> List[Category]:
        """Get all subcategories of a category"""
        return db.query(Category).filter(Category.parent_id == category_id).all()

    def update_category(
        self, db: Session, category_id: int, category_in: CategoryUpdate
    ) -> Category:
        """Update category"""
        return self.update(db, category_id, category_in)

    def delete_category(self, db: Session, category_id: int) -> None:
        """Delete category"""
        self.delete(db, category_id)


class ProductQueryBuilder:
    """
    Builder pattern for constructing product queries.
    Provides fluent interface for filtering products.
    """

    def __init__(self, db: Session):
        self.db = db
        self.query = db.query(Product).filter(Product.is_active == True)

    def filter_by_categories(self, categories_id: Optional[List[int]]):
        """Add category filter"""
        if categories_id:
            self.query = self.query.filter(Product.category_id.in_(categories_id))
        return self

    def filter_by_brands(self, brands_id: Optional[List[int]]):
        """Add brand filter"""
        if brands_id:
            self.query = self.query.filter(Product.brand_id.in_(brands_id))
        return self

    def filter_by_search(self, search: Optional[str]):
        """Add text search filter"""
        if search:
            self.query = self.query.filter(Product.name.ilike(f"%{search}%"))
        return self

    def with_joins(self):
        """Add eager loading for relationships"""
        self.query = self.query.options(
            joinedload(Product.category), joinedload(Product.brand)
        )
        return self

    def get_results(self, skip: int = 0, limit: int = 100) -> tuple[List[Product], int]:
        """Execute query and return results with total count"""
        total = self.query.count()
        products = self.query.offset(skip).limit(limit).all()
        return products, total


class ProductSearchStrategy:
    """
    Strategy pattern for different search implementations.
    Encapsulates search algorithm.
    """

    @staticmethod
    def search_multi_field(
        db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[Product], int]:
        """
        Search across multiple fields with joins.
        Searches: name, description, SKU, EAN, category name, brand name
        """
        search_pattern = f"%{search_term}%"

        query = (
            db.query(Product)
            .outerjoin(Category, Product.category_id == Category.id)
            .outerjoin(Brand, Product.brand_id == Brand.id)
            .filter(Product.is_active == True)
            .filter(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.sku.ilike(search_pattern),
                    Product.ean.ilike(search_pattern),
                    Category.name.ilike(search_pattern),
                    Brand.name.ilike(search_pattern),
                )
            )
            .options(joinedload(Product.category), joinedload(Product.brand))
            .distinct()
        )

        total = query.count()
        products = query.offset(skip).limit(limit).all()
        return products, total


class ProductService:
    """
    Product service with business logic.
    Uses Builder and Strategy patterns for complex queries.
    """

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        """Create a new product with category validation"""
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
        categories_id: Optional[List[int]] = None,
        brands_id: Optional[List[int]] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Product], int]:
        """
        Get products with filters using Builder pattern.
        Returns (products, total_count)
        """
        builder = ProductQueryBuilder(db)
        return (
            builder.filter_by_categories(categories_id)
            .filter_by_brands(brands_id)
            .filter_by_search(search)
            .get_results(skip, limit)
        )

    @staticmethod
    def get_product(db: Session, slug: str) -> Product:
        """Get product by slug"""
        product = db.query(Product).filter(Product.slug == slug).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    @staticmethod
    def update_product(db: Session, slug: str, product_in: ProductUpdate) -> Product:
        """Update product"""
        product = ProductService.get_product(db, slug)
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
    def delete_product(db: Session, slug: str) -> None:
        """Delete product"""
        product = ProductService.get_product(db, slug)
        db.delete(product)
        db.commit()

    @staticmethod
    def delete_all_products(db: Session) -> int:
        """Delete all products from database. Returns count of deleted products."""
        count = db.query(Product).count()
        db.query(Product).delete()
        db.commit()
        return count

    @staticmethod
    def search_products(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Product], int]:
        """
        Search products using Strategy pattern.
        Returns (products, total_count)
        """
        return ProductSearchStrategy.search_multi_field(db, query, skip, limit)

    @staticmethod
    def import_products_from_csv(
        db: Session, csv_file: BinaryIO, batch_size: int = 50
    ) -> CSVImportResult:
        """
        Import products from CSV file in batches.

        Expected CSV columns:
        - sku (optional)
        - ean (optional)
        - name (required)
        - description (optional)
        - price (required)
        - offer_price (optional)
        - stock (optional, default: 0)
        - is_always_in_stock (optional, default: false)
        - max_per_buy (optional)
        - weight (optional)
        - units_per_package (optional, default: 1)
        - category (required) - category name, will be created if doesn't exist
        - brand (optional) - brand name, will be created if doesn't exist
        - image_url (optional)
        - slug (required)
        - is_active (optional, default: true)
        """
        errors: List[CSVImportError] = []
        successful = 0
        total_rows = 0

        category_cache: Dict[str, int] = {}
        brand_cache: Dict[str, int] = {}

        try:
            content = csv_file.read()
            csv_text = content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(csv_text))

            required_columns = {"name", "price", "category", "slug"}
            if csv_reader.fieldnames:
                missing_columns = required_columns - set(csv_reader.fieldnames)
                if missing_columns:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required columns: {', '.join(missing_columns)}",
                    )

            batch = []
            for row_num, row in enumerate(csv_reader, start=2):
                total_rows += 1

                try:
                    category_name = row["category"].strip()
                    if not category_name:
                        raise ValueError("Category name cannot be empty")

                    if category_name not in category_cache:
                        category = (
                            db.query(Category)
                            .filter(Category.name == category_name)
                            .first()
                        )

                        if not category:
                            category_slug = (
                                category_name.lower()
                                .replace(" ", "-")
                                .replace("_", "-")
                            )
                            base_slug = category_slug
                            counter = 1
                            while (
                                db.query(Category)
                                .filter(Category.slug == category_slug)
                                .first()
                            ):
                                category_slug = f"{base_slug}-{counter}"
                                counter += 1

                            category = Category(
                                name=category_name,
                                slug=category_slug,
                                description=None,
                                parent_id=None,
                            )
                            db.add(category)
                            db.flush()

                        category_cache[category_name] = category.id

                    category_id = category_cache[category_name]

                    brand_id = None
                    brand_name = row.get("brand", "").strip()
                    if brand_name:
                        if brand_name not in brand_cache:
                            brand = (
                                db.query(Brand).filter(Brand.name == brand_name).first()
                            )

                            if not brand:
                                brand_slug = (
                                    brand_name.lower()
                                    .replace(" ", "-")
                                    .replace("_", "-")
                                )
                                base_slug = brand_slug
                                counter = 1
                                while (
                                    db.query(Brand)
                                    .filter(Brand.slug == brand_slug)
                                    .first()
                                ):
                                    brand_slug = f"{base_slug}-{counter}"
                                    counter += 1

                                brand = Brand(
                                    name=brand_name, slug=brand_slug, description=None
                                )
                                db.add(brand)
                                db.flush()

                            brand_cache[brand_name] = brand.id

                        brand_id = brand_cache[brand_name]

                    product_data = {
                        "name": row["name"].strip(),
                        "price": float(row["price"]),
                        "offer_price": float(row["offer_price"]) if row.get("offer_price", "").strip() else None,
                        "category_id": category_id,
                        "slug": row["slug"].strip(),
                        "sku": row.get("sku", "").strip() or None,
                        "ean": row.get("ean", "").strip() or None,
                        "description": row.get("description", "").strip() or None,
                        "stock": int(row.get("stock", 0)),
                        "is_always_in_stock": row.get(
                            "is_always_in_stock", "false"
                        ).lower()
                        in ("true", "1", "yes"),
                        "max_per_buy": (
                            int(row["max_per_buy"]) if row.get("max_per_buy") else None
                        ),
                        "weight": float(row["weight"]) if row.get("weight") else None,
                        "units_per_package": int(row.get("units_per_package", 1)),
                        "brand_id": brand_id,
                        "image_url": row.get("image_url", "").strip() or None,
                        "is_active": row.get("is_active", "true").lower()
                        in ("true", "1", "yes"),
                    }

                    if product_data["sku"]:
                        existing_sku = (
                            db.query(Product)
                            .filter(Product.sku == product_data["sku"])
                            .first()
                        )
                        if existing_sku:
                            raise ValueError(
                                f"Product with SKU '{product_data['sku']}' already exists"
                            )

                    if product_data["ean"]:
                        existing_ean = (
                            db.query(Product)
                            .filter(Product.ean == product_data["ean"])
                            .first()
                        )
                        if existing_ean:
                            raise ValueError(
                                f"Product with EAN '{product_data['ean']}' already exists"
                            )

                    existing_slug = (
                        db.query(Product)
                        .filter(Product.slug == product_data["slug"])
                        .first()
                    )
                    if existing_slug:
                        raise ValueError(
                            f"Product with slug '{product_data['slug']}' already exists"
                        )

                    batch.append(Product(**product_data))

                    if len(batch) >= batch_size:
                        db.add_all(batch)
                        db.commit()
                        successful += len(batch)
                        batch = []

                except (ValueError, KeyError) as e:
                    errors.append(
                        CSVImportError(row=row_num, data=dict(row), error=str(e))
                    )
                except Exception as e:
                    errors.append(
                        CSVImportError(
                            row=row_num,
                            data=dict(row),
                            error=f"Unexpected error: {str(e)}",
                        )
                    )

            if batch:
                db.add_all(batch)
                db.commit()
                successful += len(batch)

        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid file encoding. Please use UTF-8 encoded CSV file.",
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error processing CSV file: {str(e)}"
            )

        failed = len(errors)
        message = f"Import completed: {successful} products imported successfully"
        if failed > 0:
            message += f", {failed} products failed"

        return CSVImportResult(
            total_rows=total_rows,
            successful=successful,
            failed=failed,
            errors=errors,
            message=message,
        )
