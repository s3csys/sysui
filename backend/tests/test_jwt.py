import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
import jwt

from app.core.security.jwt import create_access_token, create_refresh_token, verify_token
from app.models.token import TokenPayload
from app.core.config import settings


class TestJWT:
    """Tests for JWT token functionality"""
    
    def test_create_access_token(self):
        """Test creating an access token"""
        # Setup
        subject = {"sub": 1, "username": "testuser"}
        
        # Execute
        token = create_access_token(subject=subject)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        
        # Decode token to verify contents
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        assert decoded["sub"] == 1
        assert decoded["username"] == "testuser"
        assert decoded["type"] == "access"
        assert "exp" in decoded
    
    def test_create_refresh_token(self):
        """Test creating a refresh token"""
        # Setup
        subject = 1
        
        # Execute
        token = create_refresh_token(subject=subject)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        
        # Decode token to verify contents
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        assert decoded["sub"] == 1
        assert decoded["type"] == "refresh"
        assert "exp" in decoded
    
    def test_verify_token_valid(self):
        """Test verifying a valid token"""
        # Setup
        payload = {"sub": 1, "exp": datetime.utcnow() + timedelta(minutes=15), "type": "access"}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Execute
        result = verify_token(token, "access")
        
        # Assert
        assert result is not None
        assert isinstance(result, TokenPayload)
        assert result.sub == 1
        assert result.type == "access"
    
    def test_verify_token_expired(self):
        """Test verifying an expired token"""
        # Setup
        payload = {"sub": 1, "exp": datetime.utcnow() - timedelta(minutes=15), "type": "access"}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Execute
        result = verify_token(token, "access")
        
        # Assert
        assert result is None
    
    def test_verify_token_wrong_type(self):
        """Test verifying a token with wrong type"""
        # Setup
        payload = {"sub": 1, "exp": datetime.utcnow() + timedelta(minutes=15), "type": "access"}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # Execute
        result = verify_token(token, "refresh")
        
        # Assert
        assert result is None
    
    def test_verify_token_invalid(self):
        """Test verifying an invalid token"""
        # Setup
        token = "invalid.token.string"
        
        # Execute
        result = verify_token(token, "access")
        
        # Assert
        assert result is None