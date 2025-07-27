from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List

from app.core.security.password import validate_password


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    
    @validator("password")
    def validate_password_strength(cls, v):
        error = validate_password(v)
        if error:
            raise ValueError(error)
        return v
    
    @validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not v.isalnum() and not "_" in v:
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    role: str
    
    class Config:
        orm_mode = True


class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str


class TOTPSetupResponse(BaseModel):
    """TOTP setup response schema"""
    secret: str
    uri: str


class TOTPVerifyRequest(BaseModel):
    """TOTP verification request schema"""
    token: str = Field(..., min_length=6, max_length=8)


class TOTPVerifyResponse(BaseModel):
    """TOTP verification response schema"""
    backup_codes: List[str]


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str
    
    @validator("new_password")
    def validate_password_strength(cls, v):
        error = validate_password(v)
        if error:
            raise ValueError(error)
        return v