from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List

from app.models.user import User, UserRole
from app.models.permission import Permission
from app.models.user_permission import UserPermission
from app.api.auth.dependencies import require_admin, require_permission
from app.api.auth.auth import get_current_active_verified_user
from app.api.auth.schemas import (
    PermissionList, 
    UserPermissions, 
    AddPermissionRequest, 
    RemovePermissionRequest,
    PermissionCheckResponse
)
from app.core.security import log_audit_event


router = APIRouter()


@router.get("/permissions", response_model=PermissionList)
async def list_permissions(current_user: User = Depends(require_permission(Permission.VIEW_SYSTEM_SETTINGS))):
    """
    List all available permissions in the system.
    
    Requires: VIEW_SYSTEM_SETTINGS permission
    """
    permissions = Permission.get_all_permissions()
    return {"permissions": permissions}


@router.get("/users/{user_id}/permissions", response_model=UserPermissions)
async def get_user_permissions(user_id: int, current_user: User = Depends(require_permission(Permission.VIEW_USERS)), request: Request = None):
    """
    Get permissions for a specific user.
    
    Requires: VIEW_USERS permission
    """
    # TODO: Replace with actual database query
    # This is a placeholder implementation
    from app.db.session import get_db
    db = next(get_db())
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Get permissions
    role_permissions = Permission.get_role_permissions(user.role.value)
    custom_permissions = set(user.custom_permissions)
    all_permissions = role_permissions.union(custom_permissions)
    
    # Log audit event
    log_audit_event(
        action="view_user_permissions",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="user",
        resource_id=user_id,
        request=request
    )
    
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value,
        "role_permissions": role_permissions,
        "custom_permissions": custom_permissions,
        "all_permissions": all_permissions
    }


@router.post("/users/permissions/add", status_code=status.HTTP_200_OK)
async def add_permission_to_user(request_data: AddPermissionRequest, current_user: User = Depends(require_permission(Permission.CHANGE_USER_ROLE)), request: Request = None):
    """
    Add a custom permission to a user.
    
    Requires: CHANGE_USER_ROLE permission
    """
    # TODO: Replace with actual database query
    # This is a placeholder implementation
    from app.db.session import get_db
    db = next(get_db())
    
    # Validate permission
    if request_data.permission not in Permission.get_all_permissions():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission: {request_data.permission}"
        )
    
    # Get user
    user = db.query(User).filter(User.id == request_data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Add permission if not already present
    if request_data.permission not in user.custom_permissions:
        user.custom_permissions.add(request_data.permission)
        db.commit()
    
    # Log audit event
    log_audit_event(
        action="add_user_permission",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="user",
        resource_id=request_data.user_id,
        details={"permission": request_data.permission},
        request=request
    )
    
    return {"message": f"Permission {request_data.permission} added to user {user.username}"}


@router.post("/users/permissions/remove", status_code=status.HTTP_200_OK)
async def remove_permission_from_user(request_data: RemovePermissionRequest, current_user: User = Depends(require_permission(Permission.CHANGE_USER_ROLE)), request: Request = None):
    """
    Remove a custom permission from a user.
    
    Requires: CHANGE_USER_ROLE permission
    """
    # TODO: Replace with actual database query
    # This is a placeholder implementation
    from app.db.session import get_db
    db = next(get_db())
    
    # Get user
    user = db.query(User).filter(User.id == request_data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Remove permission if present
    if request_data.permission in user.custom_permissions:
        user.custom_permissions.remove(request_data.permission)
        db.commit()
    
    # Log audit event
    log_audit_event(
        action="remove_user_permission",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="user",
        resource_id=request_data.user_id,
        details={"permission": request_data.permission},
        request=request
    )
    
    return {"message": f"Permission {request_data.permission} removed from user {user.username}"}


@router.get("/users/permissions/check/{permission}", response_model=PermissionCheckResponse)
async def check_permission(permission: str, current_user: User = Depends(get_current_active_verified_user)):
    """
    Check if the current user has a specific permission.
    
    This endpoint can be used by the frontend to determine if certain UI elements should be shown.
    """
    has_permission = current_user.has_permission(permission)
    
    return {
        "has_permission": has_permission,
        "permission": permission,
        "user_id": current_user.id
    }