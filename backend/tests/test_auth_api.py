import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.db import get_db
from app.models.user import User, UserRole
from app.models.token import Token


@pytest.fixture
def app():
    """Create a test FastAPI application"""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client for the application"""
    return TestClient(app)


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
    user.full_name = "Test User"
    user.hashed_password = "hashed_password"
    user.is_active = True
    user.is_verified = True
    user.role = UserRole.USER
    user.role.value = "user"
    user.is_2fa_enabled = False
    return user


@pytest.fixture
def override_get_db(app, mock_db):
    """Override the get_db dependency"""
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides = {}


class TestAuthAPI:
    """Tests for authentication API endpoints"""
    
    def test_register_endpoint(self, client, mock_db, override_get_db):
        """Test user registration endpoint"""
        # Setup
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "newuser"
        mock_user.email = "new@example.com"
        mock_user.full_name = "New User"
        mock_user.is_active = True
        mock_user.is_verified = False
        mock_user.role.value = "user"
        mock_user.verification_token = "verification_token"
        
        # Mock AuthService.create_user
        with patch("app.api.auth.auth.AuthService.create_user", return_value=mock_user), \
             patch("app.api.auth.auth.email_service.send_verification_email"):
            # Execute
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "SecurePassword123!",
                    "full_name": "New User"
                }
            )
            
            # Assert
            assert response.status_code == 201
            assert response.json()["username"] == "newuser"
            assert response.json()["email"] == "new@example.com"
            assert response.json()["full_name"] == "New User"
            assert response.json()["is_verified"] is False
    
    def test_login_endpoint(self, client, mock_db, mock_user, override_get_db):
        """Test user login endpoint"""
        # Setup
        access_token = "access_token"
        refresh_token = "refresh_token"
        
        # Mock AuthService.authenticate_user and create_tokens
        with patch("app.api.auth.auth.AuthService.authenticate_user", return_value=mock_user), \
             patch("app.api.auth.auth.AuthService.create_tokens", return_value=(access_token, refresh_token)):
            # Execute
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "testuser",
                    "password": "password"
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["access_token"] == access_token
            assert response.json()["refresh_token"] == refresh_token
            assert response.json()["token_type"] == "bearer"
    
    def test_verify_email_endpoint(self, client, mock_db, override_get_db):
        """Test email verification endpoint"""
        # Mock AuthService.verify_email
        with patch("app.api.auth.auth.AuthService.verify_email", return_value=True):
            # Execute
            response = client.post(
                "/api/v1/auth/verify-email",
                json={
                    "token": "verification_token"
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["message"] == "Email verified successfully"
    
    def test_refresh_token_endpoint(self, client, mock_db, mock_user, override_get_db):
        """Test token refresh endpoint"""
        # Setup
        refresh_token = "refresh_token"
        new_access_token = "new_access_token"
        new_refresh_token = "new_refresh_token"
        token_data = MagicMock()
        token_data.sub = mock_user.id
        
        # Mock verify_token and AuthService.create_tokens
        with patch("app.api.auth.auth.verify_token", return_value=token_data), \
             patch("app.api.auth.auth.AuthService.create_tokens", return_value=(new_access_token, new_refresh_token)):
            # Mock database queries
            mock_db.query.return_value.filter.return_value.first.side_effect = [mock_user, MagicMock()]
            
            # Execute
            response = client.post(
                "/api/v1/auth/refresh",
                json={
                    "refresh_token": refresh_token
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["access_token"] == new_access_token
            assert response.json()["refresh_token"] == new_refresh_token
            assert response.json()["token_type"] == "bearer"