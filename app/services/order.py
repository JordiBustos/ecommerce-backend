from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from pathlib import Path
import os
import uuid
from app.models.order import Order, OrderItem, OrderStatus, PaymentReceipt
from app.models.product import Product
from app.models.cart import CartItem
from app.models.user import User
from app.models.address import Address
from app.models.physical_store import PhysicalStore
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    @staticmethod
    def create_order(db: Session, user: User, order_in: OrderCreate) -> Order:
        """Create a new order from cart or provided items"""
        # Validate that either address_id or physical_store_id is provided, not both
        if order_in.address_id and order_in.physical_store_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot specify both address_id and physical_store_id. Choose delivery or pickup.",
            )

        if not order_in.address_id and not order_in.physical_store_id:
            raise HTTPException(
                status_code=400,
                detail="Must specify either address_id (for delivery) or physical_store_id (for pickup)",
            )

        address = None
        physical_store = None
        shipping_address = None

        # Handle delivery to address
        if order_in.address_id:
            address = (
                db.query(Address)
                .filter(Address.id == order_in.address_id, Address.user_id == user.id)
                .first()
            )

            if not address:
                raise HTTPException(
                    status_code=404,
                    detail="Address not found or does not belong to user",
                )

            # Create formatted address string for backward compatibility
            shipping_address = f"{address.address_line1}, {address.city}, {address.postal_code}, {address.country}"

        # Handle pickup at physical store
        if order_in.physical_store_id:
            physical_store = (
                db.query(PhysicalStore)
                .filter(
                    PhysicalStore.id == order_in.physical_store_id,
                    PhysicalStore.is_active == True,
                )
                .first()
            )

            if not physical_store:
                raise HTTPException(
                    status_code=404, detail="Physical store not found or is not active"
                )

            # Create store info string for backward compatibility
            shipping_address = f"Pickup at {physical_store.name}, {physical_store.address_line1}, {physical_store.city}"

        total_amount = 0
        order_items_data = []

        for item in order_in.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404, detail=f"Product {item.product_id} not found"
                )

            if not product.is_always_in_stock and product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.name}",
                )

            if item.quantity > product.max_per_buy:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot purchase more than {product.max_per_buy} units of {product.name}",
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
            address_id=order_in.address_id,
            physical_store_id=order_in.physical_store_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status=OrderStatus.PENDING,
            replacement_criterion=order_in.replacement_criterion,
            comment=order_in.comment,
        )

        # Snapshot address data if delivery
        if address:
            db_order.snapshot_full_name = address.full_name
            db_order.snapshot_country = address.country
            db_order.snapshot_postal_code = address.postal_code
            db_order.snapshot_province = address.province
            db_order.snapshot_city = address.city
            db_order.snapshot_address_line1 = address.address_line1
            db_order.snapshot_address_line2 = address.address_line2
            db_order.snapshot_phone_number = address.phone_number

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

    @staticmethod
    async def upload_receipt(
        db: Session, order_id: int, user: User, file: UploadFile
    ) -> Order:
        """Upload payment receipt for an order (image or PDF) - supports multiple receipts"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to upload receipt for this order",
            )

        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
            "application/pdf",
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed. Allowed types: images (JPEG, JPG, PNG, WebP) and PDF",
            )

        max_size = 10 * 1024 * 1024  # 10MB in bytes
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > max_size:
            raise HTTPException(status_code=400, detail=f"File size exceeds 10MB limit")

        upload_dir = Path("uploads/receipts")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename

        try:
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

        payment_receipt = PaymentReceipt(
            order_id=order.id, file_path=str(file_path), file_type=file.content_type
        )
        db.add(payment_receipt)
        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def delete_receipt(db: Session, receipt_id: int, user: User) -> None:
        """Delete a payment receipt"""
        receipt = (
            db.query(PaymentReceipt).filter(PaymentReceipt.id == receipt_id).first()
        )
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")

        order = db.query(Order).filter(Order.id == receipt.order_id).first()
        if not order or (order.user_id != user.id and not user.is_superuser):
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this receipt"
            )

        if os.path.exists(receipt.file_path):
            try:
                os.remove(receipt.file_path)
            except Exception:
                pass

        db.delete(receipt)
        db.commit()
