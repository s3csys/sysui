import pytest
from app.core.security.password import get_password_hash, verify_password, validate_password


class TestPassword:
    """Tests for password security functionality"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        # Setup
        password = "SecurePassword123!"
        
        # Execute
        hashed = get_password_hash(password)
        
        # Assert
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)
    
    def test_password_validation_valid(self):
        """Test validation of valid passwords"""
        # Valid passwords
        valid_passwords = [
            "SecurePassword123!",
            "Another-Valid-Pass1",
            "Complex_P@ssw0rd",
            "Abcd1234!@#$"
        ]
        
        # Execute and Assert
        for password in valid_passwords:
            assert validate_password(password) is None
    
    def test_password_validation_too_short(self):
        """Test validation of too short passwords"""
        # Setup
        password = "Short1!"
        
        # Execute
        result = validate_password(password)
        
        # Assert
        assert result is not None
        assert "length" in result.lower()
    
    def test_password_validation_no_uppercase(self):
        """Test validation of passwords without uppercase letters"""
        # Setup
        password = "lowercase123!"
        
        # Execute
        result = validate_password(password)
        
        # Assert
        assert result is not None
        assert "uppercase" in result.lower()
    
    def test_password_validation_no_lowercase(self):
        """Test validation of passwords without lowercase letters"""
        # Setup
        password = "UPPERCASE123!"
        
        # Execute
        result = validate_password(password)
        
        # Assert
        assert result is not None
        assert "lowercase" in result.lower()
    
    def test_password_validation_no_digit(self):
        """Test validation of passwords without digits"""
        # Setup
        password = "NoDigitsHere!"
        
        # Execute
        result = validate_password(password)
        
        # Assert
        assert result is not None
        assert "digit" in result.lower()
    
    def test_password_validation_no_special(self):
        """Test validation of passwords without special characters"""
        # Setup
        password = "NoSpecialChars123"
        
        # Execute
        result = validate_password(password)
        
        # Assert
        assert result is not None
        assert "special" in result.lower()