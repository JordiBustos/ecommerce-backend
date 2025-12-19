from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_user, get_current_superuser
from app.models.user import User
from app.services.coupon import CouponService
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponListResponse,
    CouponApply,
    CouponValidationResponse
)

router = APIRouter()


@router.get("/", response_model=CouponListResponse)
def list_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    List all coupons (admin only)
    """
    coupons, total = CouponService.get_all(db, skip=skip, limit=limit, is_active=is_active)
    return CouponListResponse(coupons=coupons, total=total)


@router.get("/my-coupons", response_model=CouponListResponse)
def get_my_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all coupons available for the current user
    """
    coupons = CouponService.get_user_coupons(db, current_user.id)
    return CouponListResponse(coupons=coupons, total=len(coupons))


@router.get("/{coupon_id}", response_model=CouponResponse)
def get_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get a specific coupon by ID (admin only)
    """
    coupon = CouponService.get_by_id(db, coupon_id)
    return coupon


@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Create a new coupon (admin only)
    """
    coupon = CouponService.create(db, coupon_data)
    return coupon


@router.put("/{coupon_id}", response_model=CouponResponse)
def update_coupon(
    coupon_id: int,
    coupon_data: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Update an existing coupon (admin only)
    """
    coupon = CouponService.update(db, coupon_id, coupon_data)
    return coupon


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a coupon (admin only)
    """
    CouponService.delete(db, coupon_id)
    return None


@router.post("/validate", response_model=CouponValidationResponse)
def validate_coupon(
    coupon_apply: CouponApply,
    order_total: float = Query(..., gt=0, description="Total order amount before discount"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate if a coupon can be used for the current user and order total
    """
    is_valid, message, discount_amount, coupon = CouponService.validate_coupon(
        db=db,
        code=coupon_apply.code,
        user_id=current_user.id,
        order_total=order_total
    )
    
    return CouponValidationResponse(
        valid=is_valid,
        message=message,
        discount_amount=discount_amount,
        coupon=coupon
    )
