from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash


class UserService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
        """Update user information"""
        if user_update.email and user_update.email != user.email:
            existing_user = UserService.get_user_by_email(db, user_update.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            user.email = user_update.email

        if user_update.username and user_update.username != user.username:
            existing_user = UserService.get_user_by_username(db, user_update.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = user_update.username

        if user_update.full_name:
            user.full_name = user_update.full_name

        if user_update.dni:
            user.dni = user_update.dni

        if user_update.birth_date:
            user.birth_date = user_update.birth_date

        if user_update.gender:
            user.gender = user_update.gender

        if user_update.phone_number:
            user.phone_number = user_update.phone_number

        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)

        db.commit()
        db.refresh(user)
        return user
