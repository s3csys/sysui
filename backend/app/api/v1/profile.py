from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator

from app.db.session import get_db
from app.models.user import User
from app.api.auth.schemas import UserResponse
from app.api.auth.dependencies import get_current_active_verified_user
from app.core.security.password import get_password_hash, verify_password
from app.core.logging import log_audit_event, log_security_event

router = APIRouter()


class ProfileUpdate(BaseModel):
    """Profile update schema"""
    email: EmailStr
    full_name: str


class PasswordUpdate(BaseModel):
    """Password update schema"""
    current_password: str
    new_password: str
    
    @validator("new_password")
    def validate_password_strength(cls, v):
        from app.core.security.password import validate_password
        error = validate_password(v)
        if error:
            raise ValueError(error)
        return v


@router.put("/update", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Update user profile information.
    """
    # Check if email is being changed and if it's already taken
    if profile_data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == profile_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user information
    current_user.email = profile_data.email
    current_user.full_name = profile_data.full_name
    
    db.commit()
    db.refresh(current_user)
    
    # Log the profile update
    log_audit_event(
        action="update_profile",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="user",
        resource_id=current_user.id,
        details={"updated_fields": ["email", "full_name"]},
        request=request
    )
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        role=current_user.role.value
    )


@router.put("/update-password", status_code=status.HTTP_200_OK)
async def update_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Update user password.
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        log_security_event(
            "password_update_failed",
            {"user_id": current_user.id, "username": current_user.username, "reason": "invalid_current_password"},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    # Log the password update
    log_security_event(
        "password_updated",
        {"user_id": current_user.id, "username": current_user.username},
        request
    )
    
    return {"message": "Password updated successfully"}