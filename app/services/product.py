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


class BrandService:
    @staticmethod
    def create_brand(db: Session, brand_in: BrandCreate) -> Brand:
        """Create a new brand"""
        existing = db.query(Brand).filter(Brand.slug == brand_in.slug).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="Brand with this slug already exists"
            )

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
            raise HTTPException(
                status_code=400, detail="Category with this slug already exists"
            )

        if category_in.parent_id:
            parent = (
                db.query(Category).filter(Category.id == category_in.parent_id).first()
            )
            if not parent:
                raise HTTPException(status_code=404, detail="Parent category not found")

        category = Category(**category_in.model_dump())
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_categories(
        db: Session, skip: int = 0, limit: int = 100, parent_only: bool = False
    ) -> List[Category]:
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
