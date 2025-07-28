from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models.token import Token, TokenData, RefreshTokenRequest, SessionInfo, SessionList
from app.models.user import User
from app.services.auth import AuthService
from app.services.email import email_service
from app.core.security import verify_token, log_auth_success, log_auth_failure, log_security_event, log_security_violation, generate_fingerprint, verify_fingerprint
from app.api.auth.schemas import (
    UserCreate, 
    UserResponse, 
    EmailVerification, 
    TOTPSetupResponse, 
    TOTPVerifyRequest,
    TOTPVerifyResponse,
    PasswordResetRequest,
    PasswordResetConfirm
)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), request: Request = None) -> User:
    """
    Get the current user from the token.
    
    Args:
        token: JWT token
        db: Database session
        request: FastAPI request object for fingerprint verification
        
    Returns:
        User: The current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Generate fingerprint from user agent if available
    fingerprint = None
    ip_address = None
    if request:
        fingerprint = generate_fingerprint(request.headers.get("user-agent"))
        ip_address = request.client.host if request.client else None
    
    token_data = verify_token(token, "access", fingerprint, ip_address)
    if not token_data:
        if request:
            log_security_violation(
                "token_validation_failure",
                {"reason": "Invalid token or fingerprint mismatch"},
                request
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        if request:
            log_security_violation(
                "token_validation_failure",
                {"reason": "User not found"},
                request
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        if request:
            log_security_violation(
                "token_validation_failure",
                {"reason": "User inactive", "user_id": user.id, "username": user.username},
                request
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current user and verify that they are active and verified.
    
    Args:
        current_user: The current user
        
    Returns:
        User: The current active and verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


async def check_2fa_required(current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme), request: Request = None) -> User:
    """
    Check if 2FA is required for the current user.
    
    Args:
        current_user: The current user
        token: JWT token
        request: FastAPI request object for fingerprint verification
        
    Returns:
        User: The current user
        
    Raises:
        HTTPException: If 2FA is required but not verified
    """
    # Generate fingerprint from user agent if available
    fingerprint = None
    ip_address = None
    if request:
        fingerprint = generate_fingerprint(request.headers.get("user-agent"))
        ip_address = request.client.host if request.client else None
    
    token_data = verify_token(token, "access", fingerprint, ip_address)
    if not token_data:
        if request:
            log_security_violation(
                "token_validation_failure",
                {"reason": "Invalid token or fingerprint mismatch", "user_id": current_user.id, "username": current_user.username},
                request
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if 2FA is required but not verified
    if current_user.is_2fa_enabled and not token_data.is_2fa_verified:
        if request:
            log_security_violation(
                "2fa_verification_required",
                {"user_id": current_user.id, "username": current_user.username},
                request
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Create user
    user = AuthService.create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )
    
    # Send verification email
    await email_service.send_verification_email(
        email_to=user.email,
        username=user.username,
        token=user.verification_token
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role.value
    )


@router.post("/verify-email", response_model=dict)
async def verify_email(verification: EmailVerification, db: Session = Depends(get_db), request: Request = None):
    """
    Verify a user's email address.
    """
    success = AuthService.verify_email(db=db, token=verification.token)
    if not success:
        log_security_event(
            "email_verification_failure",
            {"token": "[redacted]"},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",  # Generic error message for security
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"message": "Email verified successfully"}


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return an access token.
    """
    user = AuthService.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    
    if not user:
        log_auth_failure(form_data.username, "invalid_credentials", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",  # Generic error message for security
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is verified
    if not user.is_verified:
        log_auth_failure(form_data.username, "email_not_verified", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",  # Generic error message for security
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user agent and IP address
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    # Create tokens
    access_token, refresh_token = AuthService.create_tokens(
        user=user,
        user_agent=user_agent,
        ip_address=ip_address,
        db=db
    )
    
    # Log successful login
    log_auth_success(user.username, user.id, request)
    
    # Return tokens
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an access token using a refresh token.
    """
    # Generate fingerprint from user agent if available
    user_agent = request.headers.get("user-agent")
    fingerprint = generate_fingerprint(user_agent)
    
    # Get IP address from request
    ip_address = request.client.host if request.client else None
    
    # Verify refresh token with fingerprint and IP address
    token_data = verify_token(refresh_request.refresh_token, "refresh", fingerprint, ip_address)
    if not token_data:
        log_security_violation(
            "refresh_token_validation_failure",
            {"reason": "Invalid token or fingerprint mismatch"},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user or not user.is_active:
        log_security_violation(
            "refresh_token_validation_failure",
            {"reason": "User not found or inactive", "user_id": token_data.sub},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if refresh token is in database
    session = db.query(User.Session).filter(
        User.Session.user_id == user.id,
        User.Session.refresh_token == refresh_request.refresh_token,
        User.Session.is_active == True
    ).first()
    
    if not session:
        log_security_violation(
            "refresh_token_validation_failure",
            {"reason": "Token not found in active sessions", "user_id": user.id, "username": user.username},
            request
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user agent and IP address
    ip_address = request.client.host if request.client else None
    
    # Log successful token refresh
    log_security_event(
        "token_refresh",
        {"user_id": user.id, "username": user.username},
        request
    )
    
    # Invalidate old refresh token
    session.is_active = False
    db.commit()
    
    # Create new tokens with fingerprint
    access_token, refresh_token = AuthService.create_tokens(
        user=user,
        user_agent=user_agent,
        ip_address=ip_address,
        db=db
    )
    
    # Return tokens
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/2fa/setup", response_model=TOTPSetupResponse)
async def setup_2fa(
    current_user: User = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db)
):
    """
    Set up 2FA for the current user.
    """
    secret, uri = AuthService.setup_2fa(db=db, user_id=current_user.id)
    
    return TOTPSetupResponse(
        secret=secret,
        uri=uri
    )


@router.post("/2fa/verify-setup", response_model=TOTPVerifyResponse)
async def verify_2fa_setup(
    verify_request: TOTPVerifyRequest,
    current_user: User = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db)
):
    """
    Verify 2FA setup for the current user.
    """
    backup_codes = AuthService.verify_2fa_setup(
        db=db,
        user_id=current_user.id,
        token=verify_request.token
    )
    
    return TOTPVerifyResponse(
        backup_codes=backup_codes
    )


@router.post("/2fa/verify", response_model=Token)
async def verify_2fa(
    verify_request: TOTPVerifyRequest,
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Verify a 2FA token during login.
    """
    # Generate fingerprint from user agent if available
    fingerprint = None
    user_agent = request.headers.get("user-agent")
    if user_agent:
        fingerprint = generate_fingerprint(user_agent)
    
    # Get IP address from request
    ip_address = request.client.host if request.client else None
    
    # Verify access token with fingerprint and IP address
    token_data = verify_token(token, "access", fingerprint, ip_address)
    if not token_data:
        log_security_event(
            "invalid_token",
            {"token_type": "access"},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user or not user.is_active:
        log_security_event(
            "user_not_found_or_inactive",
            {"user_id": token_data.sub},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify 2FA token
    if not AuthService.verify_2fa(db=db, user_id=user.id, token=verify_request.token):
        log_auth_failure(user.username, "invalid_2fa_token", request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user agent and IP address
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    # Create new tokens with 2FA verified
    token_data = AuthService.get_token_data(user=user, is_2fa_verified=True)
    access_token = create_access_token(subject=token_data.dict(), fingerprint=fingerprint, ip_address=ip_address)
    refresh_token = create_refresh_token(subject=user.id, fingerprint=fingerprint, ip_address=ip_address)
    
    # Store refresh token
    AuthService.store_refresh_token(
        db=db,
        user_id=user.id,
        refresh_token=refresh_token,
        user_agent=user_agent,
        ip_address=ip_address
    )
    
    # Log successful 2FA verification
    log_auth_success(user.username, user.id, request)
    
    # Return tokens
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/2fa/disable")
async def disable_2fa(
    current_user: User = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Disable 2FA for the current user.
    """
    success = AuthService.disable_2fa(db=db, user_id=current_user.id)
    if not success:
        log_security_event(
            "2fa_disable_failure",
            {"user_id": current_user.id, "username": current_user.username},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful 2FA disabling
    log_security_event(
        "2fa_disabled",
        {"user_id": current_user.id, "username": current_user.username},
        request
    )
    
    return {"message": "2FA disabled successfully"}


@router.get("/sessions", response_model=SessionList)
async def get_sessions(
    current_user: User = Depends(get_current_active_verified_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Get active sessions for the current user.
    """
    # Get refresh token from request
    # Get IP address from request if available
    ip_address = request.client.host if hasattr(request, 'client') and request.client else None
    
    # Generate fingerprint from user agent if available
    fingerprint = None
    if hasattr(request, 'headers'):
        user_agent = request.headers.get("user-agent")
        if user_agent:
            fingerprint = generate_fingerprint(user_agent)
    
    token_data = verify_token(token, "access", fingerprint, ip_address)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get sessions
    sessions = AuthService.get_user_sessions(db=db, user_id=current_user.id)
    
    # Convert to response model
    session_info_list = [
        SessionInfo(
            id=session.id,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            created_at=session.created_at,
            expires_at=session.expires_at,
            is_current=getattr(session, "is_current", False)
        )
        for session in sessions
    ]
    
    return SessionList(sessions=session_info_list)


@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: int,
    current_user: User = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Terminate a session for the current user.
    """
    success = AuthService.terminate_session(db=db, session_id=session_id, user_id=current_user.id)
    if not success:
        log_security_event(
            "session_termination_attempt",
            {"user_id": current_user.id, "session_id": session_id, "status": "not_found"},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Log session termination
    log_security_event(
        "session_terminated",
        {"user_id": current_user.id, "session_id": session_id},
        request
    )
    
    return {"message": "Session terminated successfully"}


@router.delete("/sessions")
async def terminate_all_sessions(
    current_user: User = Depends(get_current_active_verified_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Terminate all sessions for the current user except the current one.
    """
    # Get refresh token from request
    # Get IP address from request if available
    ip_address = request.client.host if request and request.client else None
    
    # Generate fingerprint from user agent if available
    fingerprint = None
    if request:
        user_agent = request.headers.get("user-agent")
        if user_agent:
            fingerprint = generate_fingerprint(user_agent)
    
    token_data = verify_token(token, "access", fingerprint, ip_address)
    if not token_data:
        log_security_event(
            "invalid_token",
            {"token_type": "access"},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Terminate all sessions except current one
    count = AuthService.terminate_all_sessions(
        db=db,
        user_id=current_user.id,
        except_token=token_data.refresh_token
    )
    
    # Log session termination
    log_security_event(
        "all_sessions_terminated",
        {"user_id": current_user.id, "count": count},
        request
    )
    
    return {"message": f"{count} sessions terminated successfully"}


@router.post("/reset-password")
async def reset_password(
    reset_request: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request a password reset.
    """
    # Find user by email
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # Log attempt with non-existent email
        log_security_event(
            "password_reset_attempt",
            {"email": reset_request.email, "status": "email_not_found"},
            request,
            "warning"
        )
        # Don't reveal that the email doesn't exist
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    db.commit()
    
    # Send reset email
    await email_service.send_password_reset_email(
        email_to=user.email,
        username=user.username,
        token=reset_token
    )
    
    # Log successful password reset request
    log_security_event(
        "password_reset_requested",
        {"user_id": user.id, "username": user.username},
        request
    )
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password/confirm")
async def reset_password_confirm(
    reset_confirm: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Confirm a password reset.
    """
    # Find user by reset token
    user = db.query(User).filter(
        User.reset_token == reset_confirm.token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        log_security_event(
            "password_reset_confirm",
            {"status": "invalid_token"},
            request,
            "warning"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_confirm.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    
    # Terminate all sessions
    AuthService.terminate_all_sessions(db=db, user_id=user.id)
    
    db.commit()
    
    # Log successful password reset
    log_security_event(
        "password_reset_completed",
        {"user_id": user.id, "username": user.username},
        request
    )
    
    return {"message": "Password reset successfully"}