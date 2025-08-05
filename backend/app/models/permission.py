from enum import Enum, auto
from typing import List, Set, Dict, Optional
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base import Base
from app.models.user_permission import user_permission_association


class PermissionEnum(str, Enum):
    """Enum representing granular permissions in the system"""
    
    # User management permissions
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    CHANGE_USER_ROLE = "change_user_role"
    
    # Resource management permissions
    VIEW_RESOURCES = "view_resources"
    CREATE_RESOURCE = "create_resource"
    EDIT_RESOURCES = "edit_resources"  # Fixed to match documentation
    DELETE_RESOURCES = "delete_resources"  # Fixed to match documentation
    
    # System management permissions
    VIEW_SYSTEM_SETTINGS = "view_system_settings"
    EDIT_SYSTEM_SETTINGS = "edit_system_settings"
    
    # Audit permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    @classmethod
    def get_role_permissions(cls, role_name: str) -> Set[str]:
        """Get the set of permissions for a given role.
        
        Args:
            role_name: The name of the role (admin, editor, viewer)
            
        Returns:
            Set[str]: A set of permission names for the role
        """
        role_permissions = {
            "admin": {
                cls.VIEW_USERS, cls.CREATE_USER, cls.EDIT_USER, cls.DELETE_USER, cls.CHANGE_USER_ROLE,
                cls.VIEW_RESOURCES, cls.CREATE_RESOURCE, cls.EDIT_RESOURCES, cls.DELETE_RESOURCES,
                cls.VIEW_SYSTEM_SETTINGS, cls.EDIT_SYSTEM_SETTINGS,
                cls.VIEW_AUDIT_LOGS
            },
            "editor": {
                cls.VIEW_USERS,
                cls.VIEW_RESOURCES, cls.CREATE_RESOURCE, cls.EDIT_RESOURCES,
                cls.VIEW_SYSTEM_SETTINGS
            },
            "viewer": {
                cls.VIEW_RESOURCES,
                cls.VIEW_SYSTEM_SETTINGS
            }
        }
        
        return role_permissions.get(role_name.lower(), set())
    
    @classmethod
    def get_all_permissions(cls) -> List[str]:
        """Get a list of all available permissions.
        
        Returns:
            List[str]: A list of all permission names
        """
        return [perm.value for perm in cls]


class Permission(Base):
    """SQLAlchemy model for permissions"""
    
    __tablename__ = "permissions"
    
    # Override id from Base with None to avoid having two primary keys
    id = None
    
    # Use name as the primary key with autoincrement=False and nullable=False explicitly set
    name = Column(String(50), primary_key=True, nullable=False, autoincrement=False)
    users = relationship(
        "User", 
        secondary=user_permission_association, 
        back_populates="custom_permissions",
        primaryjoin="Permission.name == user_permission_association.c.permission_name",
        secondaryjoin="user_permission_association.c.user_id == User.id"
    )
    
    def __init__(self, name: str):
        self.name = name
        # No need to set permission_enum here as it's computed dynamically
    
    # Store the enum value in a private attribute
    _permission_enum = None
    
    @property
    def permission_enum(self) -> Optional[PermissionEnum]:
        try:
            return PermissionEnum(self.name)
        except ValueError:
            return None
            
    @permission_enum.setter
    def permission_enum(self, value):
        # This is just a placeholder to avoid errors
        # The actual value is always computed from name
        pass
    
    def __repr__(self):
        return f"<Permission {self.name}>"