from fastapi import HTTPException, Request
from enum import Enum
from typing import Optional, Dict, Any

# Mock UserRole enum
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

# Mock security logging function
def log_security_violation(event_type: str, details: Dict[str, Any], request: Optional[Request] = None) -> None:
    """Mock function for logging security violations"""
    pass

# Mock role-based access control dependencies
async def require_role(required_role: UserRole, user: Any, request: Optional[Request] = None) -> Any:
    """Check if user has the required role"""
    if not hasattr(user, 'role') or not isinstance(user.role, UserRole):
        if request:
            log_security_violation(
                "invalid_role",
                {
                    "user_id": user.id,
                    "username": user.username,
                    "user_role": getattr(user.role, 'value', 'unknown'),
                    "required_role": required_role.value
                },
                request
            )
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Admin can access everything
    if user.role == UserRole.ADMIN:
        return user
    
    # Editor can access Editor and Viewer resources
    if user.role == UserRole.EDITOR and required_role in [UserRole.EDITOR, UserRole.VIEWER]:
        return user
    
    # Viewer can only access Viewer resources
    if user.role == UserRole.VIEWER and required_role == UserRole.VIEWER:
        return user
    
    # Log security violation
    if request:
        log_security_violation(
            "insufficient_permissions",
            {
                "user_id": user.id,
                "username": user.username,
                "user_role": user.role.value,
                "required_role": required_role.value
            },
            request
        )
    
    raise HTTPException(status_code=403, detail="Insufficient permissions")

async def require_admin(user: Any, request: Optional[Request] = None) -> Any:
    """Check if user has admin role"""
    return await require_role(UserRole.ADMIN, user, request)

async def require_editor(user: Any, request: Optional[Request] = None) -> Any:
    """Check if user has editor or admin role"""
    return await require_role(UserRole.EDITOR, user, request)

async def require_viewer(user: Any, request: Optional[Request] = None) -> Any:
    """Check if user has any valid role"""
    return await require_role(UserRole.VIEWER, user, request)