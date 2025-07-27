import pytest
import pyotp
from unittest.mock import patch

from app.core.security.totp import (
    generate_totp_secret,
    get_totp_uri,
    verify_totp,
    generate_backup_codes
)


class TestTOTP:
    """Tests for TOTP 2FA functionality"""
    
    def test_generate_totp_secret(self):
        """Test generating a TOTP secret"""
        # Execute
        secret = generate_totp_secret()
        
        # Assert
        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) == 32  # Base32 encoded secret is 32 characters
        
        # Verify it's a valid base32 string that can be used with pyotp
        totp = pyotp.TOTP(secret)
        assert totp.now() is not None
    
    def test_get_totp_uri(self):
        """Test generating a TOTP URI for QR code"""
        # Setup
        secret = generate_totp_secret()
        username = "testuser"
        
        # Execute
        uri = get_totp_uri(secret, username)
        
        # Assert
        assert uri is not None
        assert isinstance(uri, str)
        assert uri.startswith("otpauth://totp/")
        assert username in uri
        assert f"secret={secret}" in uri
    
    def test_verify_totp_valid(self):
        """Test verifying a valid TOTP token"""
        # Setup
        secret = generate_totp_secret()
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        # Execute
        result = verify_totp(secret, token)
        
        # Assert
        assert result is True
    
    def test_verify_totp_invalid(self):
        """Test verifying an invalid TOTP token"""
        # Setup
        secret = generate_totp_secret()
        
        # Execute
        result = verify_totp(secret, "123456")  # Random invalid token
        
        # Assert
        assert result is False
    
    def test_generate_backup_codes(self):
        """Test generating backup codes"""
        # Execute
        plain_codes, hashed_codes = generate_backup_codes()
        
        # Assert
        assert plain_codes is not None
        assert hashed_codes is not None
        assert isinstance(plain_codes, list)
        assert isinstance(hashed_codes, list)
        assert len(plain_codes) == 10  # Default is 10 backup codes
        assert len(hashed_codes) == 10
        
        # Verify each plain code is 8 characters
        for code in plain_codes:
            assert isinstance(code, str)
            assert len(code) == 8
        
        # Verify each hashed code is a bcrypt hash
        for hashed in hashed_codes:
            assert isinstance(hashed, str)
            assert hashed.startswith("$2")  # bcrypt hash prefix