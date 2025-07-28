from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from typing import List, Optional, Set, TYPE_CHECKING, Any

from app.models.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.permission import Permission


# Association table for many-to-many relationship between users and permissions
user_permission_association = Table(
    'user_permission_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    Column('permission_name', String(50), ForeignKey('permissions.name', ondelete="CASCADE"), primary_key=True)
)


class UserPermission:
    """Helper class for user permission operations"""
    
    @staticmethod
    def get_user_permissions(user: "User") -> Set[str]:
        """Get all permissions for a user (role-based + custom)"""
        # Import here to avoid circular imports
        from app.models.user import UserRole
        from app.models.permission import PermissionEnum
        
        # Get role-based permissions
        role_permissions = UserRole.get_role_permissions(user.role)
        
        # Combine with custom permissions
        all_permissions = set(role_permissions)
        if user.custom_permissions:
            # Extract permission names from Permission objects
            custom_permission_names = set()
            for perm in user.custom_permissions:
                if hasattr(perm, 'permission_enum') and perm.permission_enum:
                    custom_permission_names.add(perm.permission_enum)
                else:
                    custom_permission_names.add(perm.name)
            all_permissions.update(custom_permission_names)
            
        return all_permissions
    
    @staticmethod
    def has_permission(user: "User", permission: str) -> bool:
        """Check if a user has a specific permission"""
        # Import here to avoid circular imports
        from app.models.user import UserRole
        from app.models.permission import PermissionEnum
        
        # First check if the permission is granted by the user's role
        if user.role == UserRole.ADMIN:
            return True  # Admin has all permissions
        
        # Check if the permission is in the role's permissions
        role_permissions = UserRole.get_role_permissions(user.role)
        if permission in role_permissions:
            return True
        
        # Finally check custom permissions
        if user.custom_permissions:
            # Check if the permission name is in the user's custom permissions
            return any(perm.name == permission or 
                      (hasattr(perm, 'permission_enum') and 
                       perm.permission_enum == permission) 
                      for perm in user.custom_permissions)
        return False