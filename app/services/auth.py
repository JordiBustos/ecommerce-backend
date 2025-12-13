from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, Token


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        """Register a new user"""
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=400, detail="User with this username already exists"
            )

        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """Authenticate user and return user object"""
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> Token:
        """Create access token for authenticated user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def login_user(db: Session, username: str, password: str) -> Token:
        """Login user and return access token"""
        user = AuthService.authenticate_user(db, username, password)
        return AuthService.create_access_token_for_user(user)

    @staticmethod
    def refresh_token(db: Session, username: str, password: str) -> Token:
        """Refresh access token for user"""
        user = AuthService.authenticate_user(db, username, password)
        return AuthService.create_access_token_for_user(user)
