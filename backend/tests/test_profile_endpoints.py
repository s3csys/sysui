import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.api.v1.profile import router as profile_router
from app.main import app


# Mock router for testing
app.include_router(profile_router, prefix="/profile", tags=["profile"])


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.hashed_password = "hashed_password"
    user.is_active = True
    user.is_verified = True
    user.role = UserRole.VIEWER
    user.role.value = "viewer"
    return user


@pytest.fixture
def override_get_current_user(app, mock_user):
    """Override the get_current_active_verified_user dependency"""
    from app.api.auth.dependencies import get_current_active_verified_user
    
    app.dependency_overrides[get_current_active_verified_user] = lambda: mock_user
    yield
    app.dependency_overrides = {}


@pytest.fixture
def override_get_db(app, mock_db):
    """Override the get_db dependency"""
    from app.db.session import get_db
    
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides = {}


class TestProfileEndpoints:
    """Tests for profile API endpoints"""
    
    def test_update_profile(self, client, mock_user, mock_db, override_get_current_user, override_get_db):
        """Test profile update endpoint"""
        # Setup
        new_email = "updated@example.com"
        new_name = "Updated User"
        
        # Mock database query for email check
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        response = client.put(
            "/profile/update",
            json={
                "email": new_email,
                "full_name": new_name
            }
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["email"] == new_email
        assert response.json()["full_name"] == new_name
        
        # Verify user object was updated
        assert mock_user.email == new_email
        assert mock_user.full_name == new_name
        assert mock_db.commit.called
        assert mock_db.refresh.called
    
    def test_update_profile_email_taken(self, client, mock_user, mock_db, override_get_current_user, override_get_db):
        """Test profile update with already taken email"""
        # Setup
        new_email = "taken@example.com"
        
        # Mock database query to simulate email already taken
        existing_user = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        # Execute
        response = client.put(
            "/profile/update",
            json={
                "email": new_email,
                "full_name": "New Name"
            }
        )
        
        # Assert
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
        
        # Verify user object was not updated
        assert mock_user.email != new_email
        assert not mock_db.commit.called
    
    def test_update_password(self, client, mock_user, mock_db, override_get_current_user, override_get_db):
        """Test password update endpoint"""
        # Setup
        current_password = "current_password"
        new_password = "NewPassword123!"
        
        # Mock password verification
        with patch("app.api.v1.profile.verify_password", return_value=True), \
             patch("app.api.v1.profile.get_password_hash", return_value="new_hashed_password"):
            
            # Execute
            response = client.put(
                "/profile/update-password",
                json={
                    "current_password": current_password,
                    "new_password": new_password
                }
            )
            
            # Assert
            assert response.status_code == 200
            assert response.json()["message"] == "Password updated successfully"
            
            # Verify password was updated
            assert mock_user.hashed_password == "new_hashed_password"
            assert mock_db.commit.called
    
    def test_update_password_incorrect_current(self, client, mock_user, mock_db, override_get_current_user, override_get_db):
        """Test password update with incorrect current password"""
        # Setup
        current_password = "wrong_password"
        new_password = "NewPassword123!"
        
        # Mock password verification to fail
        with patch("app.api.v1.profile.verify_password", return_value=False):
            
            # Execute
            response = client.put(
                "/profile/update-password",
                json={
                    "current_password": current_password,
                    "new_password": new_password
                }
            )
            
            # Assert
            assert response.status_code == 400
            assert "Incorrect current password" in response.json()["detail"]
            
            # Verify password was not updated
            assert mock_user.hashed_password != "new_hashed_password"
            assert not mock_db.commit.called