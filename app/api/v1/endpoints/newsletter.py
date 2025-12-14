from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_superuser, get_current_user, get_db
from app.models.user import User
from app.schemas.newsletter import (
    NewsletterSubscribe,
    NewsletterSubscriber as NewsletterSubscriberSchema,
    NewsletterSubscribeResponse,
)
from app.services.newsletter import NewsletterService
from app.services.email import EmailService

router = APIRouter()


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
async def subscribe_to_newsletter(
    subscription: NewsletterSubscribe, request: Request, db: Session = Depends(get_db)
):
    """
    Subscribe to the newsletter.
    Sends a verification email to confirm the subscription.
    """
    subscriber = NewsletterService.subscribe(db, subscription.email)

    base_url = str(request.base_url).rstrip("/")

    await EmailService.send_verification_email(
        email=subscriber.email, token=subscriber.verification_token, base_url=base_url
    )

    return NewsletterSubscribeResponse(
        message="Verification email sent. Please check your inbox to confirm your subscription.",
        email=subscriber.email,
    )


@router.get("/verify")
async def verify_newsletter_subscription(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Verify newsletter subscription using the token from the email.
    """
    subscriber = NewsletterService.verify_subscription(db, token)

    await EmailService.send_welcome_email(subscriber.email)

    return {
        "message": "Your subscription has been confirmed! Thank you for subscribing.",
        "email": subscriber.email,
    }


@router.delete("/unsubscribe")
def unsubscribe_from_newsletter(
    subscription: NewsletterSubscribe, db: Session = Depends(get_db)
):
    """
    Unsubscribe from the newsletter.
    """
    NewsletterService.unsubscribe(db, subscription.email)

    return {
        "message": "You have been unsubscribed from the newsletter.",
        "email": subscription.email,
    }


@router.get("/status")
def check_subscription_status(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Check if the current user is subscribed to the newsletter.
    Returns subscription status and validation status.
    """
    return NewsletterService.get_subscription_status(db, current_user.email)


@router.get("/subscribers", response_model=List[NewsletterSubscriberSchema])
def get_all_subscribers(
    validated_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get all newsletter subscribers (admin only).
    Set validated_only=true to get only confirmed subscribers.
    """
    return NewsletterService.get_all_subscribers(db, validated_only, skip, limit)
