from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.base import Base


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    validated = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, unique=True, nullable=False)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)
