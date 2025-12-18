from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    # Force load roles relationship
    len(user.roles)
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.
    Useful for endpoints that have different behavior for authenticated vs anonymous users.
    """
    if token is None:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None
    # Force load roles relationship
    len(user.roles)
    return user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# Role-based dependency factories
class RoleChecker:
    """
    Dependency class to check if user has required role(s).
    Can be used as a dependency in route handlers.
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Initialize with list of allowed role slugs.
        
        Args:
            allowed_roles: List of role slugs that are allowed access
        """
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if current user has any of the allowed roles.
        Superusers always have access.
        """
        # Superusers bypass role checks
        if current_user.is_superuser:
            return current_user
        
        # Check if user has any of the allowed roles
        if not current_user.has_any_role(self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User doesn't have required role. Required: {', '.join(self.allowed_roles)}"
            )
        
        return current_user


# Pre-defined role checkers for common use cases
def get_wholesale_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user has wholesale role"""
    checker = RoleChecker(["wholesale", "distributor"])
    return checker(current_user)


def get_vip_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user has VIP role"""
    checker = RoleChecker(["vip-customer"])
    return checker(current_user)


def get_business_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is a business customer"""
    checker = RoleChecker(["wholesale", "distributor", "retail-partner", "corporate"])
    return checker(current_user)
