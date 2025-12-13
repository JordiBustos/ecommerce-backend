from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class NewsletterSubscribe(BaseModel):
    email: EmailStr


class NewsletterSubscriber(BaseModel):
    id: int
    email: str
    validated: bool
    subscribed_at: datetime
    validated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsletterSubscribeResponse(BaseModel):
    message: str
    email: str
