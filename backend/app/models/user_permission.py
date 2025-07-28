from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from typing import List, Optional, Set, TYPE_CHECKING, Any

from app.models.base import Base
from app.models.permission import Permission

# Avoid circular imports
if TYPE_CHECKING:
    from app.models.user import User


# Association table for many-to-many relationship between users and permissions
user_permission_association = Table(
    'user_permission',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    Column('permission', String(50), primary_key=True)
)


class UserPermission:
    """Helper class for user permission operations"""
    
    @staticmethod
    def get_user_permissions(user: "User") -> Set[str]:
        """Get all permissions for a user (role-based + custom)"""
        # Import here to avoid circular imports
        from app.models.user import UserRole
        
        # Get role-based permissions
        role_permissions = UserRole.get_role_permissions(user.role)
        
        # Combine with custom permissions
        all_permissions = set(role_permissions)
        if user.custom_permissions:
            all_permissions.update(user.custom_permissions)
            
        return all_permissions
    
    @staticmethod
    def has_permission(user: "User", permission: str) -> bool:
        """Check if a user has a specific permission"""
        # Import here to avoid circular imports
        from app.models.user import UserRole
        
        # First check if the permission is granted by the user's role
        if user.role == UserRole.ADMIN:
            return True  # Admin has all permissions
        
        # Check if the permission is in the role's permissions
        role_permissions = UserRole.get_role_permissions(user.role)
        if permission in role_permissions:
            return True
        
        # Finally check custom permissions
        return permission in user.custom_permissions if user.custom_permissions else False