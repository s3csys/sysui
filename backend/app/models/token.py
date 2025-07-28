from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload model"""
    sub: Optional[str] = None
    exp: int = Field(..., description="Expiration timestamp")
    type: str = Field(..., description="Token type (access or refresh)")
    fgp: Optional[str] = Field(None, description="Token fingerprint based on user agent or device info")


class TokenData(BaseModel):
    """Token data model with user information"""
    user_id: int
    username: str
    email: str
    role: str
    is_2fa_enabled: bool
    is_2fa_verified: bool = False


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str


class SessionInfo(BaseModel):
    """Session information model"""
    id: int
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    is_current: bool = False


class SessionList(BaseModel):
    """List of active sessions"""
    sessions: List[SessionInfo]