import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from app.models.user import User, UserRole
from app.models.permission import PermissionEnum, Permission
from app.api.auth.dependencies import require_permission, require_all_permissions


# Mock User class for testing
class MockUser:
    def __init__(self, id=1, username="testuser", role=UserRole.VIEWER, custom_permissions=None):
        self.id = id
        self.username = username
        self.role = role
        self.custom_permissions = custom_permissions or set()
    
    def get_permissions(self):
        role_permissions = PermissionEnum.get_role_permissions(self.role.value)
        all_permissions = set(role_permissions)
        
        # Extract permission names from Permission objects in custom_permissions
        for perm in self.custom_permissions:
            if isinstance(perm, Permission):
                all_permissions.add(perm.name)
            else:
                all_permissions.add(perm)
                
        return all_permissions
    
    def has_permission(self, permission):
        permissions = self.get_permissions()
        return permission in permissions


# Fixtures for different user roles
@pytest.fixture
def admin_user():
    return MockUser(id=1, username="admin", role=UserRole.ADMIN)


@pytest.fixture
def editor_user():
    return MockUser(id=2, username="editor", role=UserRole.EDITOR)


@pytest.fixture
def viewer_user():
    return MockUser(id=3, username="viewer", role=UserRole.VIEWER)


@pytest.fixture
def custom_permission_user():
    # Create Permission objects for the custom permissions
    view_users_perm = Permission(name=PermissionEnum.VIEW_USERS)
    edit_user_perm = Permission(name=PermissionEnum.EDIT_USER)
    
    return MockUser(
        id=4, 
        username="custom", 
        role=UserRole.VIEWER, 
        custom_permissions={view_users_perm, edit_user_perm}
    )


# Mock request for testing
@pytest.fixture
def mock_request():
    request = MagicMock()
    request.url.path = "/api/v1/admin/users"
    request.method = "GET"
    return request


# Tests for require_permission
@pytest.mark.asyncio
async def test_require_permission_admin_has_admin_permission(admin_user):
    # Admin should have admin permissions
    result = await require_permission(PermissionEnum.VIEW_USERS)(admin_user)
    assert result == admin_user


@pytest.mark.asyncio
async def test_require_permission_editor_has_editor_permission(editor_user):
    # Editor should have editor permissions
    result = await require_permission(PermissionEnum.EDIT_RESOURCES)(editor_user)
    assert result == editor_user


@pytest.mark.asyncio
async def test_require_permission_viewer_has_viewer_permission(viewer_user):
    # Viewer should have viewer permissions
    result = await require_permission(PermissionEnum.VIEW_RESOURCES)(viewer_user)
    assert result == viewer_user


@pytest.mark.asyncio
async def test_require_permission_viewer_lacks_admin_permission(viewer_user, mock_request):
    # Viewer should not have admin permissions
    with patch("app.api.auth.dependencies.log_security_violation") as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            await require_permission(PermissionEnum.VIEW_USERS)(viewer_user, mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"
        
        # Verify security violation was logged
        mock_log.assert_called_once()
        args = mock_log.call_args[0]
        assert args[0] == "insufficient_permissions"
        assert "user_id" in args[1]
        assert "username" in args[1]
        assert "user_role" in args[1]
        assert "required_permissions" in args[1]
        assert "user_permissions" in args[1]


@pytest.mark.asyncio
async def test_require_permission_custom_permissions(custom_permission_user):
    # User with custom permissions should have those permissions
    result = await require_permission(PermissionEnum.VIEW_USERS)(custom_permission_user)
    assert result == custom_permission_user
    
    result = await require_permission(PermissionEnum.EDIT_USER)(custom_permission_user)
    assert result == custom_permission_user


@pytest.mark.asyncio
async def test_require_permission_multiple_options(custom_permission_user):
    # User should pass if they have any of the required permissions
    result = await require_permission([PermissionEnum.VIEW_USERS, PermissionEnum.VIEW_AUDIT_LOGS])(custom_permission_user)
    assert result == custom_permission_user


@pytest.mark.asyncio
async def test_require_permission_multiple_options_fails(custom_permission_user, mock_request):
    # User should fail if they don't have any of the required permissions
    with patch("app.api.auth.dependencies.log_security_violation") as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            await require_permission([PermissionEnum.VIEW_AUDIT_LOGS, PermissionEnum.EDIT_SYSTEM_SETTINGS])(
                custom_permission_user, mock_request
            )
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"


# Tests for require_all_permissions
@pytest.mark.asyncio
async def test_require_all_permissions_admin(admin_user):
    # Admin should have all permissions
    result = await require_all_permissions(
        [PermissionEnum.VIEW_USERS, PermissionEnum.EDIT_USER, PermissionEnum.DELETE_USER]
    )(admin_user)
    assert result == admin_user

@pytest.mark.asyncio
async def test_require_all_permissions_success(custom_permission_user):
    # User should pass if they have all required permissions
    result = await require_all_permissions([PermissionEnum.VIEW_USERS, PermissionEnum.EDIT_USER])(
        custom_permission_user
    )
    assert result == custom_permission_user


@pytest.mark.asyncio
async def test_require_all_permissions_fails(custom_permission_user, mock_request):
    # User should fail if they don't have all required permissions
    with patch("app.api.auth.dependencies.log_security_violation") as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            await require_all_permissions(
                [PermissionEnum.VIEW_USERS, PermissionEnum.EDIT_USER, PermissionEnum.DELETE_USER]
            )(custom_permission_user, mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"
        
        # Verify security violation was logged with missing permissions
        mock_log.assert_called_once()
        args = mock_log.call_args[0]
        assert args[0] == "insufficient_permissions"
        assert "missing_permissions" in args[1]
        assert PermissionEnum.DELETE_USER in args[1]["missing_permissions"]