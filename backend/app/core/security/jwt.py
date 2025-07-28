from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.models.token import TokenPayload


ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, 
    fingerprint: Optional[str] = None, ip_address: Optional[str] = None
) -> str:
    """
    Create a new access token.
    
    Args:
        subject: The subject of the token, typically the user ID
        expires_delta: Optional expiration time delta, defaults to settings value
        fingerprint: Optional token fingerprint based on user agent or device info
        ip_address: Optional IP address of the client
        
    Returns:
        str: The encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "access",
        "iat": datetime.utcnow(),
        "iss": settings.TOKEN_ISSUER,
        "aud": settings.TOKEN_AUDIENCE
    }
    
    # Add fingerprint if provided
    if fingerprint:
        to_encode["fgp"] = fingerprint
        
    # Add IP address if provided
    if ip_address:
        to_encode["ip"] = ip_address
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, 
    fingerprint: Optional[str] = None, ip_address: Optional[str] = None
) -> str:
    """
    Create a new refresh token.
    
    Args:
        subject: The subject of the token, typically the user ID
        expires_delta: Optional expiration time delta, defaults to settings value
        fingerprint: Optional token fingerprint based on user agent or device info
        ip_address: Optional IP address of the client
        
    Returns:
        str: The encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "type": "refresh",
        "iat": datetime.utcnow(),
        "iss": settings.TOKEN_ISSUER,
        "aud": settings.TOKEN_AUDIENCE
    }
    
    # Add fingerprint if provided
    if fingerprint:
        to_encode["fgp"] = fingerprint
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str, fingerprint: Optional[str] = None, 
               current_ip: Optional[str] = None) -> Optional[TokenPayload]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: The JWT token to verify
        token_type: The expected token type ("access" or "refresh")
        fingerprint: Optional fingerprint to validate against token's fingerprint
        current_ip: Optional IP address from the current request
        
    Returns:
        Optional[TokenPayload]: The token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            audience=settings.TOKEN_AUDIENCE,
            issuer=settings.TOKEN_ISSUER
        )
        token_data = TokenPayload(**payload)
        
        # Check if token is expired
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            return None
            
        # Check token type
        if token_data.type != token_type:
            return None
        
        # Verify fingerprint if provided
        if "fgp" in payload:
            from app.core.security.fingerprint import verify_fingerprint
            token_fingerprint = payload["fgp"]
            token_ip = payload.get("ip", None)
            
            if not verify_fingerprint(token_fingerprint, fingerprint, token_ip, current_ip):
                # Potential token compromise if fingerprint or IP doesn't match
                # This could indicate token theft or session hijacking
                from app.core.security import log_security_violation
                log_security_violation(
                    "token_security_mismatch",
                    {
                        "token_type": token_type,
                        "sub": token_data.sub if hasattr(token_data, "sub") else None,
                        "suspected_compromise": True,
                        "fingerprint_provided": fingerprint is not None,
                        "ip_provided": current_ip is not None
                    },
                    None  # No request object available here
                )
                return None
            
        return token_data
    except (jwt.JWTError, ValidationError):
        return None