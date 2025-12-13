# E-Commerce Backend API

A comprehensive FastAPI-based backend for an e-commerce platform with user authentication, product management, shopping cart, order processing, and advanced pricing features.

## 🏗️ Architecture

This project follows a **clean architecture** pattern with a dedicated **service layer** that separates business logic from HTTP routing concerns.

```
HTTP Layer (Routers) → Service Layer (Business Logic) → Database Layer (Models)
```

**Key Benefits:**
- 🎯 Separation of concerns
- 🧪 Easier testing (unit tests for services, integration tests for routes)
- 🔄 Reusable business logic
- 📖 Better maintainability
- 🛡️ Type-safe interfaces

**See [SERVICE_LAYER.md](SERVICE_LAYER.md) for detailed architecture documentation.**

## ✨ Features

- 🔐 **Authentication & Authorization**: JWT-based authentication with role-based access control
- 👥 **User Management**: User registration, login, and profile management with extended fields (DNI, birth date, gender, phone)
- 📦 **Product Management**: CRUD operations for products, categories, and brands with nested subcategories
- 🏷️ **Advanced Product Fields**: SKU, EAN, weight, stock control, max per purchase, units per package
- 🎨 **Visual Assets**: Image URLs for products, categories, and brands
- 🛒 **Shopping Cart**: Add, update, and remove items from cart
- 📝 **Order Processing**: Create and manage orders with inventory tracking
- 📍 **Address Management**: Multiple shipping addresses per user with default address support
- 💰 **Price Lists**: Advanced pricing system with user assignment and role-based pricing
- ⭐ **Favorites**: Users can save favorite products for quick access
- 🔍 **Optimized Search**: Fast multi-field search across products, categories, and brands
- 📊 **Analytics**: Best-selling products endpoint with configurable limits
- ⚡ **Redis Caching**: Optional Redis integration for improved performance on frequently accessed data
- 🏪 **Store Settings**: Customizable store configuration (colors, address, hours, contact)
- � **Newsletter**: Email subscription system with verification workflow
- 📨 **Email Service**: Professional HTML emails with SMTP support (Gmail, SendGrid, Mailgun, etc.)
- �📊 **Admin Panel**: Admin endpoints for managing users, products, orders, and price lists

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (configurable for PostgreSQL in production)
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **JWT**: Authentication tokens
- **Bcrypt**: Password hashing
- **FastAPI-Mail**: Email sending with SMTP support
- **Redis**: Optional in-memory caching for improved performance

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py           # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── api.py        # API router
│   │       └── endpoints/    # HTTP layer (thin routers)
│   ├── services/             # Business logic layer
│   │   ├── auth.py          # Authentication service
│   │   ├── user.py          # User management
│   │   ├── product.py       # Products & categories
│   │   ├── cart.py          # Shopping cart
│   │   ├── order.py         # Order processing
│   │   ├── address.py       # Address management
│   │   ├── favorite.py      # Favorites management
│   │   ├── newsletter.py    # Newsletter subscriptions
│   │   └── email.py         # Email service (SMTP)
│   │   └── favorite.py      # Favorites management
│   ├── core/
│   │   ├── config.py         # Configuration
│   │   └── security.py       # Security utilities
│   ├── db/
│   │   └── base.py           # Database setup
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   └── main.py               # Application entry point
├── alembic/                  # Database migrations
├── populate_db.py            # Sample data script
├── requirements.txt
├── .env.example
├── SERVICE_LAYER.md          # Architecture documentation
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13+
- Redis (optional, for caching - see [REDIS_SETUP.md](REDIS_SETUP.md))
- SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   cd ecommerce-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # For email functionality, add SMTP settings (see EMAIL_SETUP.md)
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Populate database with sample data** (optional)
   ```bash
   python populate_db.py
   ```
   This will create:
   - 1 admin user (admin@ecommerce.com / admin123)
   - 3 regular users (password123 for all)
   - 5 categories with 18 products
   - Sample addresses, price lists, and favorites

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

The API will be available at `http://localhost:8001`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🔑 Default Admin Credentials

After running `populate_db.py`:

- **Email**: admin@ecommerce.com
- **Username**: admin
- **Password**: admin123

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user (includes dni, birth_date, gender, phone_number)
- `GET /api/v1/users/` - List all users (admin)

### Products
- `GET /api/v1/products/` - List products (with pagination and filters)
- `GET /api/v1/products/search/` - **Search products** (multi-field: name, description, SKU, EAN, category, brand)
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/` - Create product (admin)
- `PUT /api/v1/products/{id}` - Update product (admin)
- `DELETE /api/v1/products/{id}` - Delete product (admin)

### Brands
- `GET /api/v1/products/brands` - List all brands
- `GET /api/v1/products/brands/{id}` - Get brand details
- `POST /api/v1/products/brands` - Create brand (admin)
- `PUT /api/v1/products/brands/{id}` - Update brand (admin)
- `DELETE /api/v1/products/brands/{id}` - Delete brand (admin)

### Categories
- `GET /api/v1/products/categories` - List categories (with nested subcategories)
- `GET /api/v1/products/categories/{id}` - Get category details with subcategories
- `POST /api/v1/products/categories` - Create category (admin)
- `PUT /api/v1/products/categories/{id}` - Update category (admin)
- `DELETE /api/v1/products/categories/{id}` - Delete category (admin)

### Best Selling Products
  - **Cached with Redis** for 5 minutes (if Redis is available)
  - Falls back to database queries if Redis is not running
- `POST /api/v1/best-selling/cache/clear` - Clear cache (admin only)
- `GET /api/v1/best-selling/` - Get top best-selling products (default: 12, max: 50)

### Cart
- `GET /api/v1/cart/` - Get user's cart
- `POST /api/v1/cart/items` - Add item to cart
- `PUT /api/v1/cart/items/{id}` - Update cart item
- `DELETE /api/v1/cart/items/{id}` - Remove item from cart
- `DELETE /api/v1/cart/` - Clear cart

### Orders
- `GET /api/v1/orders/` - List user's orders
- `GET /api/v1/orders/{id}` - Get order details
- `POST /api/v1/orders/` - Create order
- `PUT /api/v1/orders/{id}` - Update order status (admin)
- `GET /api/v1/orders/all/admin` - List all orders (admin)

### Addresses
- `GET /api/v1/addresses/` - Get all user addresses
- `GET /api/v1/addresses/{id}` - Get specific address
- `POST /api/v1/addresses/` - Create new address
- `PUT /api/v1/addresses/{id}` - Update address
- `DELETE /api/v1/addresses/{id}` - Delete address

### Price Lists (Admin Only)
- `GET /api/v1/price-lists/` - List all price lists
- `GET /api/v1/price-lists/{id}` - Get specific price list
- `POST /api/v1/price-lists/` - Create price list
- `PUT /api/v1/price-lists/{id}` - Update price list
- `DELETE /api/v1/price-lists/{id}` - Delete price list
- `POST /api/v1/price-lists/{id}/users` - Assign users to price list
- `DELETE /api/v1/price-lists/{id}/users` - Remove users from price list
- `POST /api/v1/price-lists/{id}/items` - Add product with custom price
- `PUT /api/v1/price-lists/items/{item_id}` - Update product price
- `DELETE /api/v1/price-lists/items/{item_id}` - Remove product from list

### Favorites
- `GET /api/v1/favorites/` - Get all user favorite products
- `POST /api/v1/favorites/{product_id}` - Add product to favorites
- `DELETE /api/v1/favorites/{product_id}` - Remove product from favorites

### Store Settings
- `GET /api/v1/store/` - Get store settings (public)

### Newsletter
- `POST /api/v1/newsletter/subscribe` - Subscribe email to newsletter (public)
- `GET /api/v1/newsletter/verify?token={token}` - Verify email subscription (public)
- `DELETE /api/v1/newsletter/unsubscribe?email={email}` - Unsubscribe from newsletter (public)
- `GET /api/v1/newsletter/subscribers` - List all subscribers (admin)
- `PUT /api/v1/store/` - Update store settings (admin)

## Database Models

- **User**: User accounts with authentication and extended profile (DNI, birth date, gender, phone)
- **Address**: Multiple shipping addresses per user with default address support
- **Product**: Product catalog with SKU, EAN, weight, stock control, brand relationship, and image URL
- **Brand**: Product brands with name, description, slug, logo URL, and timestamps
- **Category**: Product categories with nested subcategories (parent_id), image URLs, and hierarchy
- **CartItem**: Shopping cart items with quantity management
- **NewsletterSubscriber**: Email subscriptions with verification tokens and validation status
- **PaymentReceipt**: Multiple payment receipt uploads per order
- **Order**: Customer orders with status tracking and timestamps
- **OrderItem**: Individual items in orders with price snapshots at purchase time
- **PriceList**: Custom pricing lists for different user groups
- **PriceListItem**: Product-specific prices within a price list
- **UserFavorites**: Many-to-many relationship for favorite products
- **Store**: Store configuration (branding colors, physical address, opening hours, contact info)

- `SMTP_HOST`: Email server hostname (e.g., smtp.gmail.com)
- `SMTP_PORT`: Email server port (default: 587)
- `REDIS_HOST`: Redis server host (default: localhost) - optional
- `REDIS_PORT`: Redis server port (default: 6379) - optional
- `REDIS_DB`: Redis database number (default: 0) - optional
- `REDIS_PASSWORD`: Redis password if auth is enabled - optional
- `CACHE_TTL`: Cache expiration time in seconds (default: 300) - optional

**Email Configuration**: See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed SMTP setup instructions.

**Redis Configuration**: See [REDIS_SETUP.md](REDIS_SETUP.md) for Redis setup and caching details. Redis is completely optional - the app works perfectly without it
- `EMAILS_FROM_EMAIL`: Sender email address

**Email Configuration**: See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed SMTP setup instructions.
## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL`: Database connection string (default: sqlite:///./ecommerce.db)
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

## Development

### Populate database with sample data
```bash
python populate_db.py
```

### Create database migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Run tests
```bash
pytest
```

## Quick Start Example

1. **Start the server**
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

2. **Populate with sample data**
   ```bash
   python populate_db.py
   ```

3. **Login as admin** at http://localhost:8001/docs
   - Use `admin@ecommerce.com` / `admin123`
   - Get your access token

4. **Try the API**
   - Browse products and use the search endpoint
   - Create products with brands and categories
   - Set up price lists for different user groups
   - Assign users to price lists
   - Test the shopping cart and order flow
   - View best-selling products analytics
   - Configure store settings

## Key Features Deep Dive

### 🔍 Optimized Search Endpoint

The search endpoint (`/api/v1/products/search/`) provides fast, comprehensive product search:

```bash
# Search across products, categories, and brands
curl "http://localhost:8001/api/v1/products/search/?q=laptop&limit=20"
```

**Search Fields:**
- Product name
- Product description
- Product SKU
- Product EAN
- Category name
- Brand name

**Performance Optimizations:**
- Uses SQL JOINs for efficient querying
- Eager loads relationships to prevent N+1 queries
- Case-insensitive search with ILIKE
- Supports pagination (skip/limit)

### 📦 Advanced Product Management

Products include comprehensive fields for inventory and logistics:
- **SKU & EAN**: Unique identifiers for inventory tracking
- **Weight**: For shipping calculations
- **Stock Management**: `is_always_in_stock` flag or quantity tracking
- **Purchase Limits**: `max_per_buy` for limiting quantities
- **Packaging**: `units_per_package` for bulk items
- **Visual Assets**: Image URLs for product photos
- **Brand Association**: Link products to brands with logos
- **Category Hierarchy**: Nested subcategories for better organization

### 📧 Newsletter & Email System

Professional email subscription system with verification workflow:

**Features:**
- Email collection with validation
- Token-based email verification
- Professional HTML email templates
- Support for multiple SMTP providers (Gmail, SendGrid, Mailgun, AWS SES, etc.)
- Automatic fallback to console logging for development
- Unsubscribe functionality
- Admin dashboard for subscriber management

**Email Templates:**
- Verification email with branded styling
- Welcome email after confirmation
- Responsive HTML design

**Setup:**
```bash
# Configure SMTP in .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
```

For detailed setup instructions including Gmail App Passwords, see [EMAIL_SETUP.md](EMAIL_SETUP.md).

**Testing without SMTP:**
Leave SMTP settings empty in `.env` and emails will be logged to console with verification links for testing.

### 💰 Price List System

Flexible pricing for different customer segments:
- Create multiple price lists with custom names
- Assign specific users to price lists
- Override product prices per price list
- Automatic price selection based on user's assigned list
- Admin-only management endpoints

### ⚡ Redis Caching (Optional)

Improve performance with optional Redis caching:

**Implementation Example: Best-Selling Products**

The `/api/v1/best-selling/` endpoint demonstrates Redis caching:

- **Cache Strategy**: Stores product IDs with 5-minute TTL
- **Performance**: ~15x faster response time on cache hits (8ms vs 120ms)
- **Graceful Fallback**: Works perfectly without Redis
- **Cache Invalidation**: Admin endpoint to manually clear cache

**Setup:**
```bash
# Install Redis
sudo apt install redis-server  # Ubuntu
brew install redis             # macOS
docker run -d -p 6379:6379 redis:7-alpine  # Docker

# Configure in .env (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=300
```

**Benefits:**
- ⚡ 15x faster response times on cached queries
- 📉 Reduced database load
- 🔄 Automatic cache expiration
- 🛡️ Works without Redis (automatic fallback)

For detailed setup, monitoring, and extending caching to other endpoints, see [REDIS_SETUP.md](REDIS_SETUP.md).

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based access control (user/admin)
- CORS protection

## License

MIT
