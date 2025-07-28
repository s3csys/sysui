from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from typing import List, Optional, Set

from app.models.base import Base


# Association table for many-to-many relationship between users and permissions
user_permission_association = Table(
    'user_permission',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    Column('permission', String(50), primary_key=True)
)


class UserPermission:
    """Helper class for managing user permissions"""
    
    @staticmethod
    def get_user_permissions(user) -> Set[str]:
        """Get all permissions for a user, including role-based and custom permissions.
        
        Args:
            user: The user object
            
        Returns:
            Set[str]: A set of all permission names for the user
        """
        from app.models.permission import Permission
        
        # Get role-based permissions
        role_permissions = Permission.get_role_permissions(user.role.value)
        
        # Get custom permissions
        custom_permissions = {perm for perm in user.custom_permissions}
        
        # Combine and return all permissions
        return role_permissions.union(custom_permissions)
    
    @staticmethod
    def has_permission(user, permission: str) -> bool:
        """Check if a user has a specific permission.
        
        Args:
            user: The user object
            permission: The permission to check
            
        Returns:
            bool: True if the user has the permission, False otherwise
        """
        user_permissions = UserPermission.get_user_permissions(user)
        return permission in user_permissions