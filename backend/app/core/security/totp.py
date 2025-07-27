import pyotp
import base64
import secrets
from typing import Tuple

from app.core.config import settings


def generate_totp_secret() -> str:
    """
    Generate a new TOTP secret.
    
    Returns:
        str: Base32 encoded TOTP secret
    """
    # Generate a random secret
    secret_bytes = secrets.token_bytes(20)  # 160 bits as recommended by RFC 4226
    secret = base64.b32encode(secret_bytes).decode('utf-8')
    return secret


def get_totp_uri(secret: str, username: str) -> str:
    """
    Generate a TOTP URI for QR code generation.
    
    Args:
        secret: The TOTP secret
        username: The username to associate with the TOTP
        
    Returns:
        str: The TOTP URI for QR code generation
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=settings.TOTP_ISSUER)


def verify_totp(secret: str, token: str) -> bool:
    """
    Verify a TOTP token.
    
    Args:
        secret: The TOTP secret
        token: The TOTP token to verify
        
    Returns:
        bool: True if the token is valid, False otherwise
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token)


def generate_backup_codes(count: int = 10) -> Tuple[list, list]:
    """
    Generate backup codes for 2FA recovery.
    
    Args:
        count: Number of backup codes to generate
        
    Returns:
        Tuple[list, list]: A tuple containing the plain text codes and their hashes
    """
    from app.core.security.password import get_password_hash
    
    codes = []
    hashed_codes = []
    
    for _ in range(count):
        # Generate a random 8-character code
        code = secrets.token_hex(4).upper()
        codes.append(code)
        hashed_codes.append(get_password_hash(code))
    
    return codes, hashed_codes