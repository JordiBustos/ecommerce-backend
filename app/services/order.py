from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.cart import CartItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    @staticmethod
    def create_order(db: Session, user: User, order_in: OrderCreate) -> Order:
        """Create a new order from cart or provided items"""
        total_amount = 0
        order_items_data = []

        for item in order_in.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product {item.product_id} not found"
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.name}",
                )

            item_total = product.price * item.quantity
            total_amount += item_total
            order_items_data.append(
                {
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "price": product.price,
                }
            )

        db_order = Order(
            user_id=user.id,
            total_amount=total_amount,
            shipping_address=order_in.shipping_address,
            status=OrderStatus.PENDING,
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        for item_data in order_items_data:
            order_item = OrderItem(order_id=db_order.id, **item_data)
            db.add(order_item)

            product = (
                db.query(Product).filter(Product.id == item_data["product_id"]).first()
            )
            product.stock -= item_data["quantity"]

        db.query(CartItem).filter(CartItem.user_id == user.id).delete()

        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def get_user_orders(
        db: Session, user: User, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get all orders for a user"""
        return (
            db.query(Order)
            .filter(Order.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_order(db: Session, user: User, order_id: int) -> Order:
        """Get specific order for a user"""
        order = (
            db.query(Order)
            .filter(Order.id == order_id, Order.user_id == user.id)
            .first()
        )

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return order

    @staticmethod
    def get_all_orders(
        db: Session, user: User, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """Get all orders (admin only)"""
        if not user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to view all orders"
            )
        return db.query(Order).offset(skip).limit(limit).all()

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Order:
        """Get order by ID (admin only)"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    @staticmethod
    def update_order(
        db: Session, order_id: int, order_update: OrderUpdate, user: User
    ) -> Order:
        """Update order status or details (admin only)"""
        order = OrderService.get_order_by_id(db, order_id)
        if not order.user_id == user.id and not user.is_superuser:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this order"
            )

        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        db.commit()
        db.refresh(order)
        return order
