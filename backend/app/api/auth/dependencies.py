from fastapi import Depends, HTTPException, status, Request
from typing import List, Union

from app.models.user import User, UserRole
from app.models.permission import Permission
from app.core.security import log_security_violation
from app.api.auth.auth import get_current_active_verified_user


async def require_role(required_role: UserRole, current_user: User = Depends(get_current_active_verified_user), request: Request = None) -> User:
    """
    Dependency to check if the current user has the required role or higher privileges.
    
    Args:
        required_role: The required role
        current_user: The current user
        request: Optional FastAPI request object
        
    Returns:
        User: The current user if they have the required role or higher privileges
        
    Raises:
        HTTPException: If the user doesn't have the required role or higher privileges
    """
    # Check if user has the required role or higher privileges using the role hierarchy
    if UserRole.has_permission(current_user.role, required_role):
        return current_user
    
    # Log security violation
    if request:
        log_security_violation(
            "insufficient_permissions",
            {
                "user_id": current_user.id,
                "username": current_user.username,
                "user_role": current_user.role.value,
                "required_role": required_role.value,
                "path": request.url.path,
                "method": request.method
            },
            request
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )


async def require_admin(current_user: User = Depends(get_current_active_verified_user), request: Request = None) -> User:
    """
    Dependency to check if the current user is an admin.
    
    Args:
        current_user: The current user
        request: Optional FastAPI request object
        
    Returns:
        User: The current user if they are an admin
        
    Raises:
        HTTPException: If the user is not an admin
    """
    # Check if user has admin privileges using the role hierarchy
    if UserRole.has_permission(current_user.role, UserRole.ADMIN):
        return current_user
    
    # Log security violation
    if request:
        log_security_violation(
            "insufficient_permissions",
            {
                "user_id": current_user.id,
                "username": current_user.username,
                "user_role": current_user.role.value,
                "required_role": UserRole.ADMIN.value,
                "path": request.url.path,
                "method": request.method
            },
            request
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )


async def require_editor(current_user: User = Depends(get_current_active_verified_user), request: Request = None) -> User:
    """
    Dependency to check if the current user is an editor or admin.
    
    Args:
        current_user: The current user
        request: Optional FastAPI request object
        
    Returns:
        User: The current user if they are an editor or admin
        
    Raises:
        HTTPException: If the user is not an editor or admin
    """
    # Check if user has editor or higher privileges using the role hierarchy
    if UserRole.has_permission(current_user.role, UserRole.EDITOR):
        return current_user
    
    # Log security violation
    if request:
        log_security_violation(
            "insufficient_permissions",
            {
                "user_id": current_user.id,
                "username": current_user.username,
                "user_role": current_user.role.value,
                "required_role": UserRole.EDITOR.value,
                "path": request.url.path,
                "method": request.method
            },
            request
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )


async def require_viewer(current_user: User = Depends(get_current_active_verified_user), request: Request = None) -> User:
    """
    Dependency to check if the current user is a viewer, editor, or admin.
    
    Args:
        current_user: The current user
        request: Optional FastAPI request object
        
    Returns:
        User: The current user if they have any role
        
    Raises:
        HTTPException: If the user has no role
    """
    # Check if user has viewer or higher privileges using the role hierarchy
    if UserRole.has_permission(current_user.role, UserRole.VIEWER):
        return current_user
    
    # This should never happen as all users have at least VIEWER role by default
    # But we include it for completeness
    if request:
        log_security_violation(
            "invalid_role",
            {
                "user_id": current_user.id,
                "username": current_user.username,
                "user_role": current_user.role.value,
                "required_role": UserRole.VIEWER.value,
                "path": request.url.path,
                "method": request.method
            },
            request
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions"
    )


def require_permission(required_permission: Union[str, List[str]]):
    """
    Dependency factory to check if the current user has the required permission(s).
    
    Args:
        required_permission: The required permission or list of permissions (any one is sufficient)
        
    Returns:
        Dependency function that checks if the current user has the required permission
    """
    async def check_permission(current_user: User = Depends(get_current_active_verified_user), request: Request = None) -> User:
        # Convert single permission to list for consistent handling
        if isinstance(required_permission, str):
            required_permissions = [required_permission]
        else:
            required_permissions = required_permission
        
        # Get all user permissions (role-based + custom)
        user_permissions = current_user.get_permissions()
        
        # Check if user has any of the required permissions
        for permission in required_permissions:
            if permission in user_permissions:
                return current_user
        
        # Log security violation
        if request:
            log_security_violation(
                "insufficient_permissions",
            {
                "user_id": current_user.id,
                "username": current_user.username,
                "user_role": current_user.role.value,
                "required_permissions": required_permissions,
                "user_permissions": list(user_permissions),
                "path": request.url.path,
                "method": request.method
            },
            request
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return check_permission


def require_all_permissions(required_permissions: List[str]):
    """
    Dependency factory to check if the current user has all the required permissions.
    
    Args:
        required_permissions: List of required permissions (all are required)
        
    Returns:
        Dependency function that checks if the current user has all the required permissions
    """
    async def check_all_permissions(current_user: User = Depends(get_current_active_verified_user), request: Request = None) -> User:
        # Get all user permissions (role-based + custom)
        user_permissions = current_user.get_permissions()
        
        # Check if user has all required permissions
        missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
        
        if not missing_permissions:
            return current_user
        
        # Log security violation
        if request:
            log_security_violation(
                "insufficient_permissions",
                {
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "user_role": current_user.role.value,
                    "required_permissions": required_permissions,
                    "missing_permissions": missing_permissions,
                    "user_permissions": list(user_permissions),
                    "path": request.url.path,
                    "method": request.method
                },
                request
            )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return check_all_permissions