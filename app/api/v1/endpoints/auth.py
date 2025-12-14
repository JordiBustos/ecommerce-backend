from fastapi import APIRouter, Depends, status, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user import UserCreate, User as UserSchema, Token
from app.services.auth import AuthService
from app.core.auth_security import login_tracker
from app.core.logging_config import log_security_event

router = APIRouter()


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user"""
    # Validate honeypot fields
    user_in.validate_honeypot(request)

    # Log registration attempt
    client_ip = request.client.host if request.client else "unknown"
    log_security_event(
        "info",
        "User registration attempt",
        {"username": user_in.username, "email": user_in.email, "ip": client_ip},
    )

    return AuthService.register_user(db, user_in)


@router.post("/login", response_model=Token)
def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Login and receive access token"""
    username = form_data.username
    client_ip = request.client.host if request.client else "unknown"

    # Check if account is locked
    if login_tracker.is_locked(username):
        remaining = login_tracker.get_remaining_lockout_time(username)
        log_security_event(
            "warning",
            "Login attempt on locked account",
            {"username": username, "ip": client_ip, "remaining_seconds": remaining},
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked. Try again in {remaining} seconds.",
        )

    try:
        token = AuthService.login_user(db, username, form_data.password)

        # Set JWT token as HTTP-only session cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="strict",
            # No max_age = session cookie (expires when browser closes)
        )

        # Successful login - clear failed attempts
        login_tracker.record_successful_login(username)
        log_security_event(
            "info", "Successful login", {"username": username, "ip": client_ip}
        )
        return token
    except HTTPException as e:
        # Failed login - record attempt
        login_tracker.record_failed_attempt(username, client_ip)
        log_security_event(
            "warning",
            "Failed login attempt",
            {"username": username, "ip": client_ip, "error": str(e.detail)},
        )
        raise


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Refresh access token"""
    username = form_data.username
    client_ip = request.client.host if request.client else "unknown"

    # Check if account is locked
    if login_tracker.is_locked(username):
        remaining = login_tracker.get_remaining_lockout_time(username)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked. Try again in {remaining} seconds.",
        )

    try:
        token = AuthService.refresh_token(db, username, form_data.password)

        # Set JWT token as HTTP-only session cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="strict",
            # No max_age = session cookie (expires when browser closes)
        )

        log_security_event(
            "info", "Token refreshed", {"username": username, "ip": client_ip}
        )
        return token
    except HTTPException as e:
        login_tracker.record_failed_attempt(username, client_ip)
        log_security_event(
            "warning", "Failed token refresh", {"username": username, "ip": client_ip}
        )
        raise
