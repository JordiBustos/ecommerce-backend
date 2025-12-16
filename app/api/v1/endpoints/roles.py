from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_superuser
from app.schemas.role import Role, RoleBase
from app.services.role import RoleService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Role])
def get_all_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get all roles (admin only).
    """
    return RoleService.get_all_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=Role)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get a specific role by ID (admin only).
    """
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.get("/slug/{slug}", response_model=Role)
def get_role_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get a specific role by slug (admin only).
    """
    role = RoleService.get_role_by_slug(db, slug)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=Role, status_code=201)
def create_role(
    role_data: RoleBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Create a new role (admin only).
    """
    existing_role = RoleService.get_role_by_slug(db, role_data.slug)
    if existing_role:
        raise HTTPException(status_code=400, detail="Role with this slug already exists")
    
    return RoleService.create_role(db, role_data)


@router.put("/{role_id}", response_model=Role)
def update_role(
    role_id: int,
    role_data: RoleBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Update a role (admin only).
    """
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return RoleService.update_role(db, role_id, role_data)


@router.delete("/{role_id}", status_code=204)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a role (admin only).
    Cannot delete roles that are assigned to users.
    """
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if role has users
    users = RoleService.get_users_by_role(db, role_id)
    if users:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role. It is assigned to {len(users)} user(s)"
        )
    
    RoleService.delete_role(db, role_id)


@router.post("/{role_id}/users/{user_id}", response_model=dict)
def assign_role_to_user(
    role_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Assign a role to a user (admin only).
    """
    success = RoleService.assign_role_to_user(db, user_id, role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign role to user")
    
    return {"message": "Role assigned successfully"}


@router.delete("/{role_id}/users/{user_id}", response_model=dict)
def remove_role_from_user(
    role_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Remove a role from a user (admin only).
    """
    success = RoleService.remove_role_from_user(db, user_id, role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove role from user")
    
    return {"message": "Role removed successfully"}


@router.get("/{role_id}/users", response_model=List[dict])
def get_users_with_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get all users with a specific role (admin only).
    """
    role = RoleService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    users = RoleService.get_users_by_role(db, role_id)
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
        for user in users
    ]
