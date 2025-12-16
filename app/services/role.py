"""
Role Service
Provides role management and assignment functionality.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.role import Role, DEFAULT_ROLES
from app.models.user import User


class RoleService:
    """Service for managing user roles"""
    
    @staticmethod
    def get_role_by_slug(db: Session, slug: str) -> Optional[Role]:
        """Get role by slug"""
        return db.query(Role).filter(Role.slug == slug, Role.is_active == True).first()
    
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
    
    @staticmethod
    def get_all_roles(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Role]:
        """Get all roles"""
        query = db.query(Role)
        if active_only:
            query = query.filter(Role.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def ensure_default_roles_exist(db: Session) -> None:
        """
        Ensure all default roles exist in database.
        Creates them if they don't exist.
        """
        for role_data in DEFAULT_ROLES:
            existing = db.query(Role).filter(Role.slug == role_data["slug"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
        db.commit()
    
    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_id: int) -> bool:
        """
        Assign a role to a user by IDs.
        Returns True if successful, False otherwise.
        """
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            return False
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
        
        return True
    
    @staticmethod
    def assign_role_to_user_by_slug(db: Session, user: User, role_slug: str) -> User:
        """
        Assign a role to a user by slug.
        Does nothing if user already has the role.
        """
        role = RoleService.get_role_by_slug(db, role_slug)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_slug}' not found")
        
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        
        return user
    
    @staticmethod
    def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
        """Remove a role from a user by IDs. Returns True if successful."""
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            return False
        
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
        
        return True
    
    @staticmethod
    def remove_role_from_user_by_slug(db: Session, user: User, role_slug: str) -> User:
        """Remove a role from a user by slug"""
        role = RoleService.get_role_by_slug(db, role_slug)
        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{role_slug}' not found")
        
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
            db.refresh(user)
        
        return user
    
    @staticmethod
    def assign_roles_to_user(db: Session, user: User, role_slugs: List[str]) -> User:
        """Assign multiple roles to a user"""
        for role_slug in role_slugs:
            RoleService.assign_role_to_user_by_slug(db, user, role_slug)
        return user
    
    @staticmethod
    def replace_user_roles(db: Session, user: User, role_slugs: List[str]) -> User:
        """Replace all user roles with new ones"""
        # Remove all existing roles
        user.roles = []
        
        # Add new roles
        for role_slug in role_slugs:
            role = RoleService.get_role_by_slug(db, role_slug)
            if role:
                user.roles.append(role)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_users_by_role(db: Session, role_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with a specific role by role ID"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return []
        
        return (
            db.query(User)
            .join(User.roles)
            .filter(Role.id == role.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def assign_default_role(db: Session, user: User) -> User:
        """
        Assign the default 'End Consumer' role to a new user.
        Called during user registration.
        """
        return RoleService.assign_role_to_user_by_slug(db, user, "end-consumer")
    
    @staticmethod
    def create_role(db: Session, role_data) -> Role:
        """Create a new role"""
        role = Role(
            name=role_data.name,
            slug=role_data.slug,
            description=role_data.description
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_data) -> Optional[Role]:
        """Update an existing role"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None
        
        role.name = role_data.name
        role.slug = role_data.slug
        role.description = role_data.description
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Delete a role"""
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False
        
        db.delete(role)
        db.commit()
        return True
