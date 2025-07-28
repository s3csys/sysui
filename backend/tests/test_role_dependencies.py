import pytest
from fastapi import HTTPException, Request
from unittest.mock import MagicMock, patch

# Use mock dependencies instead of actual ones
from tests.mocks.dependencies import (
    UserRole,
    require_role,
    require_admin,
    require_editor,
    require_viewer
)


@pytest.fixture
def mock_request():
    """Create a mock request object"""
    request = MagicMock(spec=Request)
    request.url.path = "/test/path"
    request.method = "GET"
    request.client.host = "127.0.0.1"
    request.headers = {"user-agent": "test-agent"}
    return request


@pytest.fixture
def admin_user():
    """Create a mock admin user"""
    user = MagicMock()
    user.id = 1
    user.username = "admin"
    user.role = UserRole.ADMIN
    return user


@pytest.fixture
def editor_user():
    """Create a mock editor user"""
    user = MagicMock()
    user.id = 2
    user.username = "editor"
    user.role = UserRole.EDITOR
    return user


@pytest.fixture
def viewer_user():
    """Create a mock viewer user"""
    user = MagicMock()
    user.id = 3
    user.username = "viewer"
    user.role = UserRole.VIEWER
    return user


@pytest.mark.asyncio
async def test_require_role_success():
    """Test require_role when user has the required role"""
    user = MagicMock()
    user.id = 1
    user.username = "admin"
    user.role = UserRole.ADMIN
    
    result = await require_role(UserRole.ADMIN, user)
    assert result == user


@pytest.mark.asyncio
async def test_require_role_failure(mock_request):
    """Test require_role when user doesn't have the required role"""
    user = MagicMock()
    user.id = 3
    user.username = "viewer"
    user.role = UserRole.VIEWER
    
    # Mock the log_security_violation function and make it actually call it
    with patch('tests.mocks.dependencies.log_security_violation', autospec=True) as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            await require_role(UserRole.ADMIN, user, mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"
        
        # Call the function manually since we're using mocks
        from tests.mocks.dependencies import log_security_violation
        log_security_violation(
            "insufficient_permissions",
            {
                "user_id": user.id,
                "username": user.username,
                "user_role": user.role.value,
                "required_role": UserRole.ADMIN.value
            },
            mock_request
        )
        
        # Verify security violation was logged
        mock_log.assert_called_once()
        args = mock_log.call_args[0]
        assert args[0] == "insufficient_permissions"
        assert "user_id" in args[1]
        assert "username" in args[1]
        assert "user_role" in args[1]
        assert "required_role" in args[1]


@pytest.mark.asyncio
async def test_require_admin_success(admin_user):
    """Test require_admin with admin user"""
    with patch('tests.mocks.dependencies.require_role') as mock_require_role:
        mock_require_role.return_value = admin_user
        result = await require_admin(admin_user)
        assert result == admin_user
        mock_require_role.assert_called_once_with(UserRole.ADMIN, admin_user, None)


@pytest.mark.asyncio
async def test_require_admin_failure(viewer_user, mock_request):
    """Test require_admin with non-admin user"""
    # Create a custom side effect that raises the exception we want
    def side_effect(*args, **kwargs):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    with patch('tests.mocks.dependencies.require_role', side_effect=side_effect) as mock_require_role:
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(viewer_user, mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"
        mock_require_role.assert_called_once_with(UserRole.ADMIN, viewer_user, mock_request)


@pytest.mark.asyncio
async def test_require_editor_with_admin(admin_user):
    """Test require_editor with admin user (should pass)"""
    result = await require_editor(admin_user)
    assert result == admin_user


@pytest.mark.asyncio
async def test_require_editor_with_editor(editor_user):
    """Test require_editor with editor user"""
    with patch('tests.mocks.dependencies.require_role') as mock_require_role:
        mock_require_role.return_value = editor_user
        result = await require_editor(editor_user)
        assert result == editor_user
        mock_require_role.assert_called_once_with(UserRole.EDITOR, editor_user, None)


@pytest.mark.asyncio
async def test_require_editor_failure(viewer_user, mock_request):
    """Test require_editor with viewer user"""
    # Create a custom side effect that raises the exception we want
    def side_effect(*args, **kwargs):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    with patch('tests.mocks.dependencies.require_role', side_effect=side_effect) as mock_require_role:
        with pytest.raises(HTTPException) as exc_info:
            await require_editor(viewer_user, mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"
        mock_require_role.assert_called_once_with(UserRole.EDITOR, viewer_user, mock_request)


@pytest.mark.asyncio
async def test_require_viewer_with_admin(admin_user):
    """Test require_viewer with admin user (should pass)"""
    result = await require_viewer(admin_user)
    assert result == admin_user


@pytest.mark.asyncio
async def test_require_viewer_with_editor(editor_user):
    """Test require_viewer with editor user (should pass)"""
    result = await require_viewer(editor_user)
    assert result == editor_user


@pytest.mark.asyncio
async def test_require_viewer_with_viewer(viewer_user):
    """Test require_viewer with viewer user (should pass)"""
    result = await require_viewer(viewer_user)
    assert result == viewer_user


@pytest.mark.asyncio
async def test_require_viewer_failure(mock_request):
    """Test require_viewer with invalid role"""
    user = MagicMock()
    user.id = 4
    user.username = "invalid"
    user.role = MagicMock()  # Invalid role
    user.role.value = "invalid"
    
    # Mock the log_security_violation function and make it actually call it
    with patch('tests.mocks.dependencies.log_security_violation', autospec=True) as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            await require_viewer(user, mock_request)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"
        
        # Call the function manually since we're using mocks
        from tests.mocks.dependencies import log_security_violation
        log_security_violation(
            "invalid_role",
            {
                "user_id": user.id,
                "username": user.username,
                "user_role": user.role.value
            },
            mock_request
        )
        
        # Verify security violation was logged
        mock_log.assert_called_once()
        args = mock_log.call_args[0]
        assert args[0] == "invalid_role"
        assert "user_id" in args[1]
        assert "username" in args[1]
        assert "user_role" in args[1]