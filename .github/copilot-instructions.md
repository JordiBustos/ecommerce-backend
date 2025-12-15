# E-Commerce Backend AI Coding Instructions

## Architecture Overview

This FastAPI backend implements **Clean Architecture** with a dedicated service layer:
- **Routers** ([app/api/v1/endpoints/](app/api/v1/endpoints/)) handle HTTP concerns only
- **Services** ([app/services/](app/services/)) contain ALL business logic - routers are thin wrappers
- **Models** ([app/models/](app/models/)) define database entities via SQLAlchemy

**Critical Rule:** Business logic MUST be in services, not routers. New features require service classes.

## Key Development Patterns

### Service Layer Pattern
All business logic lives in service classes inheriting from [BaseService](app/services/base.py):
```python
# Wrong - logic in router
@router.post("/products")
def create_product(data):
    if not category_exists(data.category_id):  # Business logic in router
        raise HTTPException(...)

# Right - logic in service
def create_product(router_data):
    return ProductService.create_product(db, router_data)
```

### Design Patterns in Use
- **Repository Pattern**: [BaseService](app/services/base.py) and [SlugUniqueService](app/services/base.py) provide CRUD abstractions
  - [EntityRepository](app/services/repository.py): Generic repository with common query operations
  - [UserOwnedEntityRepository](app/services/repository.py): Extended repository for user-owned entities
- **Builder Pattern**: [ProductQueryBuilder](app/services/product.py#L98) for complex filtering
- **Strategy Pattern**: 
  - [ProductSearchStrategy](app/services/product.py#L140) for different search implementations
  - [ProductValidator](app/services/product_validator.py): Validation strategies for stock, purchase limits, product state
  - [PriceCalculator](app/services/price_calculator.py): Pricing strategies for base price and price list pricing
- **Chain of Responsibility**: [ValidationChain](app/services/product_validator.py) executes multiple validation strategies
- **Template Method**: [SlugUniqueService](app/services/base.py#L70) extends base create behavior
- **Facade Pattern**: `validate_product_and_quantity()` simplifies complex validation operations

### Redis Integration (Optional)
Redis is completely optional - see [BestSellingService](app/services/best_selling.py):
- Always include fallback to DB-only queries
- Use connection pooling pattern with error handling
- Cache keys follow `feature:param:value` convention

## Development Workflow

### Database Changes
```bash
# Create migration after model changes
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Quick Setup/Reset
```bash
python populate_db.py  # Creates admin user + sample data
uvicorn app.main:app --reload --port 8001  # Standard dev server
```

### Testing Credentials (after populate_db.py)
- Admin: `admin@ecommerce.com` / `admin123`

## Security Implementation

### Middleware Stack
[SecurityMiddleware](app/middleware/security.py) implements comprehensive security:
- Rate limiting with configurable thresholds
- IP blocking/whitelisting via database tables
- Request size limits and validation
- Security headers (HSTS, CSP) from [security_config.py](app/core/security_config.py)

### Authentication Flow
- JWT tokens via [security.py](app/core/security.py)
- User dependencies in [deps.py](app/api/deps.py): `get_current_user`, `get_current_superuser`
- Role-based access with `is_superuser` field

## Domain-Specific Conventions

### Validation & Business Rules (DRY Implementation)
**CRITICAL**: Use centralized validators - NEVER duplicate validation logic:
- **Stock Validation**: Use [ProductValidator](app/services/product_validator.py) for all stock/quantity checks
- **Price Calculation**: Use [PriceCalculator](app/services/price_calculator.py) for all pricing logic
- **Product Queries**: Use [EntityRepository](app/services/repository.py) for common database operations

```python
# Wrong - inline validation
if not product.is_always_in_stock and product.stock < quantity:
    raise HTTPException(...)

# Right - use validator
ProductValidator.validate_for_cart(product, quantity)

# Wrong - manual price calculation
total = product.price * quantity

# Right - use calculator (handles price lists)
total = PriceCalculator.calculate_item_total(product, quantity, user, db)
```

### Product Management
- **Hierarchical Categories**: Categories can have parent_id for subcategories
- **Advanced Fields**: SKU, EAN, weight, stock control, purchase limits
- **Multi-field Search**: Searches across product name, description, SKU, EAN, category, brand
- **CSV Import**: Batch processing (50 products) with brand/category auto-creation

### Pricing System
- **Price Lists**: Custom pricing for different user groups via [PriceListService](app/services/price_list.py)
- **User Assignment**: Admin can assign users to specific price lists
- **Fallback Pricing**: Uses product base price if user has no assigned price list

### Order Processing
- **Inventory Tracking**: Stock management with `is_always_in_stock` flag
- **Address Snapshots**: Orders store address copies to preserve delivery details
- **Receipt Management**: Multiple payment receipts per order via file uploads

## Configuration Patterns

### Environment Variables ([config.py](app/core/config.py))
- Database: `DATABASE_URL` (supports SQLite/PostgreSQL)
- Security: Rate limiting, password policies, CORS settings
- Email: SMTP configuration (optional - falls back to console logging)
- Redis: All optional with graceful fallback

### File Uploads
- Receipts stored in `/uploads/receipts/`
- Static file serving via FastAPI StaticFiles
- Size limits enforced by security middleware

## Testing & Development

### Development Database
SQLite by default - no external dependencies required for development.

### API Documentation
Swagger UI automatically available at `/docs` with full schema documentation.

### Error Handling
- Services use HTTPException for API errors
- Security middleware logs suspicious activity
- Email service gracefully falls back to console logging for development

## Critical Integration Points

### Database Session Management
- Use `get_db()` dependency for session handling
- All services expect `Session` parameter
- Commit/rollback handled by service methods

### Cross-Service Communication
Services are stateless and communicate via shared database state, not direct calls.

### External Dependencies
- **Email**: Optional SMTP via fastapi-mail
- **Redis**: Optional caching with connection pooling
- **File Storage**: Local filesystem via uploads directory