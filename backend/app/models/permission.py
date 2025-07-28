from enum import Enum, auto
from typing import List, Set, Dict, Optional


class Permission(str, Enum):
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
    EDIT_RESOURCE = "edit_resource"
    DELETE_RESOURCE = "delete_resource"
    
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
                cls.VIEW_RESOURCES, cls.CREATE_RESOURCE, cls.EDIT_RESOURCE, cls.DELETE_RESOURCE,
                cls.VIEW_SYSTEM_SETTINGS, cls.EDIT_SYSTEM_SETTINGS,
                cls.VIEW_AUDIT_LOGS
            },
            "editor": {
                cls.VIEW_USERS,
                cls.VIEW_RESOURCES, cls.CREATE_RESOURCE, cls.EDIT_RESOURCE,
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