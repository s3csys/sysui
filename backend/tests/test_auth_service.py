import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.auth import AuthService
from app.models.user import User, TOTPSecret, BackupCode, Session as UserSession
from app.core.security import verify_password


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user():
    """Mock user for testing"""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = "hashed_password"
    user.is_active = True
    user.is_verified = True
    user.role.value = "user"
    return user


class TestAuthService:
    """Tests for AuthService"""
    
    def test_authenticate_user_success(self, mock_db, mock_user):
        """Test successful user authentication"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Patch verify_password to return True
        with patch("app.services.auth.auth_service.verify_password", return_value=True):
            # Execute
            result = AuthService.authenticate_user(mock_db, "testuser", "password")
            
            # Assert
            assert result == mock_user
            mock_db.query.assert_called_once_with(User)
            mock_db.query.return_value.filter.assert_called_once()
    
    def test_authenticate_user_wrong_password(self, mock_db, mock_user):
        """Test authentication with wrong password"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Patch verify_password to return False
        with patch("app.services.auth.auth_service.verify_password", return_value=False):
            # Execute
            result = AuthService.authenticate_user(mock_db, "testuser", "wrong_password")
            
            # Assert
            assert result is None
    
    def test_authenticate_user_not_found(self, mock_db):
        """Test authentication with non-existent user"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        result = AuthService.authenticate_user(mock_db, "nonexistent", "password")
        
        # Assert
        assert result is None
    
    def test_create_user_success(self, mock_db):
        """Test successful user creation"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_user = MagicMock(spec=User)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Patch get_password_hash and uuid
        with patch("app.services.auth.auth_service.get_password_hash", return_value="hashed_password"), \
             patch("app.services.auth.auth_service.uuid.uuid4", return_value="verification_token"):
            # Execute
            with patch("app.services.auth.auth_service.User", return_value=mock_user):
                result = AuthService.create_user(mock_db, "testuser", "test@example.com", "password")
            
            # Assert
            assert result == mock_user
            mock_db.add.assert_called_once_with(mock_user)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)
    
    def test_create_user_username_exists(self, mock_db):
        """Test user creation with existing username"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(spec=User)
        
        # Execute and Assert
        with pytest.raises(HTTPException) as excinfo:
            AuthService.create_user(mock_db, "existing", "test@example.com", "password")
        
        assert excinfo.value.status_code == 400
        assert "Username already registered" in excinfo.value.detail
    
    def test_create_user_email_exists(self, mock_db):
        """Test user creation with existing email"""
        # Setup
        # First query returns None (username doesn't exist)
        # Second query returns a user (email exists)
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, MagicMock(spec=User)]
        
        # Execute and Assert
        with pytest.raises(HTTPException) as excinfo:
            AuthService.create_user(mock_db, "testuser", "existing@example.com", "password")
        
        assert excinfo.value.status_code == 400
        assert "Email already registered" in excinfo.value.detail