from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import secrets
from app.models.newsletter import NewsletterSubscriber


class NewsletterService:
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure random token for email verification"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def subscribe(db: Session, email: str) -> NewsletterSubscriber:
        """Subscribe an email to the newsletter"""
        existing = db.query(NewsletterSubscriber).filter(
            NewsletterSubscriber.email == email
        ).first()
        
        if existing:
            if existing.validated:
                raise HTTPException(
                    status_code=400,
                    detail="This email is already subscribed to the newsletter"
                )
            else:
                existing.verification_token = NewsletterService.generate_verification_token()
                existing.subscribed_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing
        
        verification_token = NewsletterService.generate_verification_token()
        subscriber = NewsletterSubscriber(
            email=email,
            verification_token=verification_token,
            validated=False
        )
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)
        
        return subscriber

    @staticmethod
    def verify_subscription(db: Session, token: str) -> NewsletterSubscriber:
        """Verify a newsletter subscription using the token"""
        subscriber = db.query(NewsletterSubscriber).filter(
            NewsletterSubscriber.verification_token == token
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=404,
                detail="Invalid verification token"
            )
        
        if subscriber.validated:
            raise HTTPException(
                status_code=400,
                detail="Email already verified"
            )
        
        subscriber.validated = True
        subscriber.validated_at = datetime.utcnow()
        db.commit()
        db.refresh(subscriber)
        
        return subscriber

    @staticmethod
    def unsubscribe(db: Session, email: str) -> None:
        """Unsubscribe an email from the newsletter"""
        subscriber = db.query(NewsletterSubscriber).filter(
            NewsletterSubscriber.email == email
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=404,
                detail="Email not found in newsletter subscribers"
            )
        
        db.delete(subscriber)
        db.commit()

    @staticmethod
    def get_subscription_status(db: Session, email: str) -> dict:
        """Check if an email is subscribed to the newsletter"""
        subscriber = db.query(NewsletterSubscriber).filter(
            NewsletterSubscriber.email == email
        ).first()
        
        if not subscriber:
            return {
                "subscribed": False,
                "validated": False,
                "email": email
            }
        
        return {
            "subscribed": True,
            "validated": subscriber.validated,
            "email": subscriber.email,
            "subscribed_at": subscriber.subscribed_at
        }

    @staticmethod
    def get_all_subscribers(
        db: Session, validated_only: bool = False, skip: int = 0, limit: int = 100
    ):
        """Get all newsletter subscribers (admin only)"""
        query = db.query(NewsletterSubscriber)
        
        if validated_only:
            query = query.filter(NewsletterSubscriber.validated == True)
        
        return query.offset(skip).limit(limit).all()
