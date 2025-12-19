from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, Token


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        """Register a new user with default 'End Consumer' role"""
        # Import here to avoid circular dependency
        from app.services.role import RoleService

        existing_user = db.query(User).filter(
        or_(
            User.email == user_in.email,
            User.username == user_in.username,
            User.dni == user_in.dni
        )
        ).first()

        if existing_user:
            if existing_user.email == user_in.email:
                raise HTTPException(
                    status_code=400, detail="User with this email already exists"
                )
            
            if existing_user.username == user_in.username:
                raise HTTPException(
                    status_code=400, detail="User with this username already exists"
                )
                
            if existing_user.dni == user_in.dni:
                raise HTTPException(
                    status_code=400, detail="User with this DNI already exists"
                )

        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
            is_superuser=False,
            gender=user_in.gender,
            birth_date=user_in.birth_date,
            dni=user_in.dni,
            phone_number=user_in.phone_number,
        )

        db.add(db_user)

        try:
            db.commit()
            db.refresh(db_user)

            # Assign default 'End Consumer' role to new user
            RoleService.assign_default_role(db, db_user)

        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig)
            if "users.email" in error_msg:
                raise HTTPException(
                    status_code=400, detail="User with this email already exists"
                )
            elif "users.username" in error_msg:
                raise HTTPException(
                    status_code=400, detail="User with this username already exists"
                )
            elif "users.dni" in error_msg:
                raise HTTPException(
                    status_code=400, detail="User with this DNI already exists"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Registration failed: duplicate value detected",
                )

        return db_user

    @staticmethod
    def _get_user_by_username(db: Session, username: str) -> User | None:
        """Get user by username from database"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """Authenticate user by username or email and return user object"""
        user = db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
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
