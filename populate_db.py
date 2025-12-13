"""
Populate database with sample data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.base import Base, engine
from app.models.user import User
from app.models.product import Product, Category
from app.models.address import Address
from app.models.price_list import PriceList, PriceListItem
from app.models.favorite import user_favorites
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.core.security import get_password_hash
from datetime import datetime, date


def populate_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = Session(bind=engine)

    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already populated!")
            return

        # Create Admin User
        admin = User(
            email="admin@ecommerce.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            dni="12345678A",
            birth_date=date(1990, 1, 1),
            gender="other",
            phone_number="+34 600 111 111",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)

        # Create Regular Users
        users = [
            User(
                email="john@example.com",
                username="john_doe",
                hashed_password=get_password_hash("password123"),
                full_name="John Doe",
                dni="23456789B",
                birth_date=date(1985, 5, 15),
                gender="male",
                phone_number="+34 600 222 222",
                is_active=True,
                is_superuser=False,
            ),
            User(
                email="jane@example.com",
                username="jane_smith",
                hashed_password=get_password_hash("password123"),
                full_name="Jane Smith",
                dni="34567890C",
                birth_date=date(1992, 8, 20),
                gender="female",
                phone_number="+34 600 333 333",
                is_active=True,
                is_superuser=False,
            ),
            User(
                email="bob@example.com",
                username="bob_wilson",
                hashed_password=get_password_hash("password123"),
                full_name="Bob Wilson",
                dni="45678901D",
                birth_date=date(1988, 3, 10),
                gender="male",
                phone_number="+34 600 444 444",
                is_active=True,
                is_superuser=False,
            ),
        ]
        for user in users:
            db.add(user)

        db.commit()

        # Create Categories
        categories = [
            Category(
                name="Electronics",
                description="Electronic devices and gadgets",
                slug="electronics",
            ),
            Category(
                name="Clothing", description="Fashion and apparel", slug="clothing"
            ),
            Category(name="Books", description="Books and literature", slug="books"),
            Category(
                name="Home & Garden",
                description="Home improvement and gardening",
                slug="home-garden",
            ),
            Category(
                name="Sports", description="Sports equipment and gear", slug="sports"
            ),
        ]
        for category in categories:
            db.add(category)

        db.commit()

        # Create Products
        products = [
            # Electronics
            Product(
                name="Laptop Pro 15",
                description="High-performance laptop",
                price=1299.99,
                stock=50,
                category_id=1,
                slug="laptop-pro-15",
                is_active=True,
            ),
            Product(
                name="Wireless Mouse",
                description="Ergonomic wireless mouse",
                price=29.99,
                stock=200,
                category_id=1,
                slug="wireless-mouse",
                is_active=True,
            ),
            Product(
                name="USB-C Hub",
                description="7-in-1 USB-C hub",
                price=49.99,
                stock=100,
                category_id=1,
                slug="usb-c-hub",
                is_active=True,
            ),
            Product(
                name="Mechanical Keyboard",
                description="RGB mechanical keyboard",
                price=89.99,
                stock=75,
                category_id=1,
                slug="mechanical-keyboard",
                is_active=True,
            ),
            Product(
                name="Noise Cancelling Headphones",
                description="Premium headphones",
                price=299.99,
                stock=60,
                category_id=1,
                slug="headphones",
                is_active=True,
            ),
            # Clothing
            Product(
                name="Cotton T-Shirt",
                description="Comfortable cotton t-shirt",
                price=19.99,
                stock=300,
                category_id=2,
                slug="cotton-tshirt",
                is_active=True,
            ),
            Product(
                name="Denim Jeans",
                description="Classic blue jeans",
                price=59.99,
                stock=150,
                category_id=2,
                slug="denim-jeans",
                is_active=True,
            ),
            Product(
                name="Winter Jacket",
                description="Warm winter jacket",
                price=129.99,
                stock=80,
                category_id=2,
                slug="winter-jacket",
                is_active=True,
            ),
            Product(
                name="Running Shoes",
                description="Lightweight running shoes",
                price=89.99,
                stock=120,
                category_id=2,
                slug="running-shoes",
                is_active=True,
            ),
            # Books
            Product(
                name="Python Programming",
                description="Learn Python from scratch",
                price=39.99,
                stock=100,
                category_id=3,
                slug="python-programming",
                is_active=True,
            ),
            Product(
                name="Web Development Guide",
                description="Modern web development",
                price=44.99,
                stock=80,
                category_id=3,
                slug="web-dev-guide",
                is_active=True,
            ),
            Product(
                name="Data Science Handbook",
                description="Data science fundamentals",
                price=49.99,
                stock=90,
                category_id=3,
                slug="data-science-handbook",
                is_active=True,
            ),
            # Home & Garden
            Product(
                name="Coffee Maker",
                description="Automatic coffee maker",
                price=79.99,
                stock=50,
                category_id=4,
                slug="coffee-maker",
                is_active=True,
            ),
            Product(
                name="Blender Pro",
                description="High-speed blender",
                price=69.99,
                stock=60,
                category_id=4,
                slug="blender-pro",
                is_active=True,
            ),
            Product(
                name="Garden Tool Set",
                description="Complete garden tool set",
                price=99.99,
                stock=40,
                category_id=4,
                slug="garden-tools",
                is_active=True,
            ),
            # Sports
            Product(
                name="Yoga Mat",
                description="Non-slip yoga mat",
                price=29.99,
                stock=150,
                category_id=5,
                slug="yoga-mat",
                is_active=True,
            ),
            Product(
                name="Dumbbells Set",
                description="Adjustable dumbbells",
                price=149.99,
                stock=70,
                category_id=5,
                slug="dumbbells-set",
                is_active=True,
            ),
            Product(
                name="Tennis Racket",
                description="Professional tennis racket",
                price=119.99,
                stock=50,
                category_id=5,
                slug="tennis-racket",
                is_active=True,
            ),
        ]
        for product in products:
            db.add(product)

        db.commit()

        # Create Addresses for users
        addresses = [
            Address(
                user_id=2,
                full_name="John Doe",
                country="Spain",
                province="Barcelona",
                city="Barcelona",
                postal_code="08001",
                address_line1="Carrer de la Pau, 123",
                phone_number="+34 600 222 222",
                is_default=True,
            ),
            Address(
                user_id=3,
                full_name="Jane Smith",
                country="Spain",
                province="Madrid",
                city="Madrid",
                postal_code="28001",
                address_line1="Calle Mayor, 45",
                phone_number="+34 600 333 333",
                is_default=True,
            ),
            Address(
                user_id=4,
                full_name="Bob Wilson",
                country="Spain",
                province="Valencia",
                city="Valencia",
                postal_code="46001",
                address_line1="Avenida del Puerto, 78",
                phone_number="+34 600 444 444",
                is_default=True,
            ),
        ]
        for address in addresses:
            db.add(address)

        db.commit()

        # Create Price Lists
        wholesale_price_list = PriceList(
            name="Wholesale Prices",
            description="Special pricing for wholesale customers",
            is_active=True,
            role_filter="wholesale",
        )
        db.add(wholesale_price_list)

        vip_price_list = PriceList(
            name="VIP Member Prices",
            description="Exclusive pricing for VIP members",
            is_active=True,
            role_filter="vip",
        )
        db.add(vip_price_list)

        db.commit()

        # Assign users to price lists
        wholesale_price_list.users.append(users[0])  # John
        vip_price_list.users.append(users[1])  # Jane

        # Add products to price lists with special prices
        wholesale_items = [
            PriceListItem(
                price_list_id=wholesale_price_list.id, product_id=1, price=1199.99
            ),
            PriceListItem(
                price_list_id=wholesale_price_list.id, product_id=2, price=24.99
            ),
            PriceListItem(
                price_list_id=wholesale_price_list.id, product_id=5, price=269.99
            ),
            PriceListItem(
                price_list_id=wholesale_price_list.id, product_id=7, price=49.99
            ),
        ]

        vip_items = [
            PriceListItem(price_list_id=vip_price_list.id, product_id=1, price=1249.99),
            PriceListItem(price_list_id=vip_price_list.id, product_id=5, price=279.99),
            PriceListItem(price_list_id=vip_price_list.id, product_id=8, price=119.99),
            PriceListItem(price_list_id=vip_price_list.id, product_id=17, price=139.99),
        ]

        for item in wholesale_items + vip_items:
            db.add(item)

        db.commit()

        # Add some favorites
        db.execute(user_favorites.insert().values(user_id=2, product_id=1))
        db.execute(user_favorites.insert().values(user_id=2, product_id=5))
        db.execute(user_favorites.insert().values(user_id=2, product_id=10))
        db.execute(user_favorites.insert().values(user_id=3, product_id=6))
        db.execute(user_favorites.insert().values(user_id=3, product_id=9))
        db.execute(user_favorites.insert().values(user_id=3, product_id=16))

        db.commit()

        print("✅ Database populated successfully!")
        print("\n" + "=" * 60)
        print("ADMIN CREDENTIALS")
        print("=" * 60)
        print("Email:    admin@ecommerce.com")
        print("Username: admin")
        print("Password: admin123")
        print("=" * 60)
        print("\nREGULAR USER CREDENTIALS")
        print("=" * 60)
        print("User 1:")
        print("  Email:    john@example.com")
        print("  Username: john_doe")
        print("  Password: password123")
        print("\nUser 2:")
        print("  Email:    jane@example.com")
        print("  Username: jane_smith")
        print("  Password: password123")
        print("\nUser 3:")
        print("  Email:    bob@example.com")
        print("  Username: bob_wilson")
        print("  Password: password123")
        print("=" * 60)
        print("\nDatabase contains:")
        print(f"  - 4 users (1 admin, 3 regular)")
        print(f"  - 5 categories")
        print(f"  - 18 products")
        print(f"  - 3 addresses")
        print(f"  - 2 price lists with special pricing")
        print(f"  - 6 favorite products")
        print("=" * 60)

    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_db()
