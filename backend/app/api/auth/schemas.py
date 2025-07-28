from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Set

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


class PermissionBase(BaseModel):
    """Base schema for permission operations"""
    name: str = Field(..., description="Permission name")


class PermissionList(BaseModel):
    """Schema for listing all available permissions"""
    permissions: List[str] = Field(..., description="List of all available permissions")


class UserPermissions(BaseModel):
    """Schema for user permissions"""
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
    role_permissions: Set[str] = Field(..., description="Permissions from user's role")
    custom_permissions: Set[str] = Field(..., description="Custom permissions assigned to user")
    all_permissions: Set[str] = Field(..., description="All permissions (role + custom)")


class AddPermissionRequest(BaseModel):
    """Schema for adding a permission to a user"""
    user_id: int = Field(..., description="User ID")
    permission: str = Field(..., description="Permission to add")


class RemovePermissionRequest(BaseModel):
    """Schema for removing a permission from a user"""
    user_id: int = Field(..., description="User ID")
    permission: str = Field(..., description="Permission to remove")


class PermissionCheckResponse(BaseModel):
    """Schema for permission check response"""
    has_permission: bool = Field(..., description="Whether the user has the permission")
    permission: str = Field(..., description="The permission that was checked")
    user_id: int = Field(..., description="User ID")