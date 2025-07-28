from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union

from app.db import get_db
from app.models.user import User, UserRole
from app.models.permission import PermissionEnum
from app.api.auth.dependencies import require_admin, require_editor, require_viewer, require_permission
from app.api.auth.auth import get_current_active_verified_user
from app.api.auth.schemas import UserResponse
from app.core.security.logger import log_security_event, log_audit_event

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    request: Request,
    current_user: User = Depends(require_permission(PermissionEnum.VIEW_USERS)), 
    db: Session = Depends(get_db)
):
    """
    Get all users. Requires VIEW_USERS permission (admin role by default).
    """
    users = db.query(User).all()
    
    # Log access to user list
    log_audit_event(
        action="view_user_list",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="users",
        request=request
    )
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role.value
        ) for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, 
    current_user: User = Depends(require_permission(PermissionEnum.VIEW_USERS)), 
    db: Session = Depends(get_db), 
    request: Request = None
):
    """
    Get a specific user. Requires VIEW_USERS permission (admin or editor role by default).
    """
    # Allow users to view their own profile regardless of permissions
    if user_id != current_user.id and not current_user.has_permission(PermissionEnum.VIEW_USERS):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view other users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log access to specific user
    log_audit_event(
        action="view_user_details",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="user",
        resource_id=user_id,
        request=request
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role.value
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_verified_user)):
    """
    Get current user profile. Requires any authenticated role.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        role=current_user.role.value
    )