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
- 📦 **Product Management**: CRUD operations for products and categories
- 🛒 **Shopping Cart**: Add, update, and remove items from cart
- 📝 **Order Processing**: Create and manage orders with inventory tracking
- 📍 **Address Management**: Multiple shipping addresses per user with default address support
- 💰 **Price Lists**: Advanced pricing system with user assignment and role-based pricing
- ⭐ **Favorites**: Users can save favorite products for quick access
- 🔍 **Search & Filter**: Product search and category filtering
- 📊 **Admin Panel**: Admin endpoints for managing users, products, orders, and price lists

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (configurable for PostgreSQL in production)
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **JWT**: Authentication tokens
- **Bcrypt**: Password hashing

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
│   │   ├── price_list.py    # Price list system
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
- SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   cd /home/jordi/projects/ecommerce/backend
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
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/` - Create product (admin)
- `PUT /api/v1/products/{id}` - Update product (admin)
- `DELETE /api/v1/products/{id}` - Delete product (admin)

### Categories
- `GET /api/v1/products/categories` - List categories
- `POST /api/v1/products/categories` - Create category (admin)
- `PUT /api/v1/products/categories/{id}` - Update category (admin)
- `DELETE /api/v1/products/categories/{id}` - Delete category (admin)

### Best Selling Products
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
- `PUT /api/v1/store/` - Update store settings (admin)

## Database Models

- **User**: User accounts with authentication and extended profile (DNI, birth date, gender, phone)
- **Address**: Multiple shipping addresses per user with default address support
- **Product**: Product catalog with pricing and inventory
- **Category**: Product categories
- **CartItem**: Shopping cart items
- **Order**: Customer orders with order tracking
- **OrderItem**: Individual items in orders with price snapshots
- **PriceList**: Custom pricing lists for different user groups
- **PriceListItem**: Product-specific prices within a price list
- **UserFavorites**: Many-to-many relationship for favorite products
- **Store**: Store configuration (branding, address, hours, contact info)

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
   - Create products
   - Set up price lists
   - Assign users to price lists
   - Test the shopping cart and order flow

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Role-based access control (user/admin)
- CORS protection

## License

MIT
