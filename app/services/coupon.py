from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime

from app.models.coupon import Coupon
from app.models.user import User
from app.schemas.coupon import CouponCreate, CouponUpdate
from app.services.base import BaseService


class CouponService(BaseService):
    """Service for managing coupons with business logic"""

    @staticmethod
    def get_all(
        db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> tuple[List[Coupon], int]:
        """Get all coupons with optional filtering"""
        query = db.query(Coupon)

        if is_active is not None:
            query = query.filter(Coupon.is_active == is_active)

        total = query.count()
        coupons = query.offset(skip).limit(limit).all()

        return coupons, total

    @staticmethod
    def get_by_id(db: Session, coupon_id: int) -> Coupon:
        """Get coupon by ID"""
        coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found"
            )
        return coupon

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Coupon]:
        """Get coupon by code"""
        return db.query(Coupon).filter(Coupon.code == code.upper()).first()

    @staticmethod
    def create(db: Session, coupon_data: CouponCreate) -> Coupon:
        """Create a new coupon"""
        existing = CouponService.get_by_code(db, coupon_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Coupon with code '{coupon_data.code}' already exists",
            )

        coupon = Coupon(
            code=coupon_data.code.upper(),
            description=coupon_data.description,
            discount_type=coupon_data.discount_type,
            discount_value=coupon_data.discount_value,
            min_order_amount=coupon_data.min_order_amount,
            max_uses=coupon_data.max_uses,
            max_uses_per_user=coupon_data.max_uses_per_user,
            is_active=coupon_data.is_active,
            valid_from=coupon_data.valid_from,
            valid_to=coupon_data.valid_to,
        )

        if coupon_data.assigned_user_ids:
            users = (
                db.query(User).filter(User.id.in_(coupon_data.assigned_user_ids)).all()
            )
            if len(users) != len(coupon_data.assigned_user_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more user IDs are invalid",
                )
            coupon.assigned_users = users

        db.add(coupon)
        db.commit()
        db.refresh(coupon)

        return coupon

    @staticmethod
    def update(db: Session, coupon_id: int, coupon_data: CouponUpdate) -> Coupon:
        """Update an existing coupon"""
        coupon = CouponService.get_by_id(db, coupon_id)

        if coupon_data.code and coupon_data.code.upper() != coupon.code:
            existing = CouponService.get_by_code(db, coupon_data.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Coupon with code '{coupon_data.code}' already exists",
                )
            coupon.code = coupon_data.code.upper()

        update_data = coupon_data.dict(
            exclude_unset=True, exclude={"assigned_user_ids"}
        )
        for field, value in update_data.items():
            setattr(coupon, field, value)

        if coupon_data.assigned_user_ids is not None:
            if coupon_data.assigned_user_ids:
                users = (
                    db.query(User)
                    .filter(User.id.in_(coupon_data.assigned_user_ids))
                    .all()
                )
                if len(users) != len(coupon_data.assigned_user_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more user IDs are invalid",
                    )
                coupon.assigned_users = users
            else:
                coupon.assigned_users = []

        coupon.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(coupon)

        return coupon

    @staticmethod
    def delete(db: Session, coupon_id: int) -> None:
        """Delete a coupon"""
        coupon = CouponService.get_by_id(db, coupon_id)
        db.delete(coupon)
        db.commit()

    @staticmethod
    def validate_coupon(
        db: Session, code: str, user_id: int, order_total: float
    ) -> tuple[bool, str, Optional[float], Optional[Coupon]]:
        """
        Validate if a coupon can be used
        Returns: (is_valid, message, discount_amount, coupon)
        """
        coupon = CouponService.get_by_code(db, code)

        if not coupon:
            return False, "Coupon not found", None, None

        if not coupon.is_valid():
            reasons = []
            if not coupon.is_active:
                reasons.append("Coupon is inactive")

            now = datetime.utcnow()
            if coupon.valid_from and now < coupon.valid_from:
                reasons.append(
                    f"Coupon is not valid until {coupon.valid_from.strftime('%Y-%m-%d')}"
                )

            if coupon.valid_to and now > coupon.valid_to:
                reasons.append(
                    f"Coupon expired on {coupon.valid_to.strftime('%Y-%m-%d')}"
                )

            if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
                reasons.append("Coupon usage limit reached")

            return False, "; ".join(reasons), None, None

        if not coupon.can_be_used_by_user(user_id, db):
            if coupon.assigned_users:
                user_ids = [u.id for u in coupon.assigned_users]
                if user_id not in user_ids:
                    return (
                        False,
                        "This coupon is not available for your account",
                        None,
                        None,
                    )

            if coupon.max_uses_per_user:
                return (
                    False,
                    f"You have already used this coupon the maximum number of times ({coupon.max_uses_per_user})",
                    None,
                    None,
                )

        if order_total < coupon.min_order_amount:
            return (
                False,
                f"Order total must be at least {coupon.min_order_amount} to use this coupon",
                None,
                None,
            )

        discount = coupon.calculate_discount(order_total)

        return True, "Coupon is valid", discount, coupon

    @staticmethod
    def apply_coupon_to_order(db: Session, coupon: Coupon) -> None:
        """Increment coupon usage counter"""
        coupon.current_uses += 1
        db.commit()

    @staticmethod
    def get_user_coupons(db: Session, user_id: int) -> List[Coupon]:
        """Get all coupons available for a specific user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        assigned_coupons = user.coupons

        unrestricted_coupons = (
            db.query(Coupon)
            .filter(~Coupon.assigned_users.any(), Coupon.is_active == True)
            .all()
        )

        all_coupons = list(set(assigned_coupons + unrestricted_coupons))
        valid_coupons = [c for c in all_coupons if c.is_valid()]

        return valid_coupons
