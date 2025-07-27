from passlib.context import CryptContext
from typing import Optional

# Configure the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain-text password to verify
        hashed_password: The hashed password to check against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storing.
    
    Args:
        password: The plain-text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def validate_password(password: str) -> Optional[str]:
    """
    Validate password strength.
    
    Args:
        password: The password to validate
        
    Returns:
        Optional[str]: Error message if validation fails, None if password is valid
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number"
    
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter"
    
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter"
    
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?" for char in password):
        return "Password must contain at least one special character"
    
    return None