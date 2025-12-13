from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user import UserCreate, User as UserSchema, Token
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    return AuthService.register_user(db, user_in)


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login and receive access token"""
    return AuthService.login_user(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """Refresh access token"""
    return AuthService.refresh_token(db, form_data.username, form_data.password)
