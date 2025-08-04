from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.models.user import User, TOTPSecret, BackupCode, Session as UserSession
from app.models.token import TokenData
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    generate_totp_secret,
    verify_totp,
    generate_backup_codes
)
from app.core.config import settings


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username or email and password.
        
        Args:
            db: Database session
            username: Username or email to authenticate
            password: Password to verify
            
        Returns:
            Optional[User]: The authenticated user or None if authentication fails
        """
        # Check if input is an email (contains @)
        if '@' in username:
            user = db.query(User).filter(User.email == username).first()
        else:
            user = db.query(User).filter(User.username == username).first()
            
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            username: Username for the new user
            email: Email for the new user
            password: Password for the new user
            full_name: Optional full name for the new user
            
        Returns:
            User: The created user
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create verification token
        verification_token = str(uuid.uuid4())
        
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_verified=False,  # User needs to verify email
            verification_token=verification_token
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def verify_email(db: Session, token: str) -> bool:
        """
        Verify a user's email with a verification token.
        
        Args:
            db: Database session
            token: Verification token
            
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        user = db.query(User).filter(User.verification_token == token).first()
        if not user:
            return False
        
        user.is_verified = True
        user.verification_token = None
        db.commit()
        
        return True
    
    @staticmethod
    def create_tokens(user: User, user_agent: Optional[str] = None, ip_address: Optional[str] = None, db: Session = None) -> Tuple[str, str]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: The user to create tokens for
            user_agent: Optional user agent string for session tracking
            ip_address: Optional IP address for session tracking
            db: Optional database session for storing refresh token
            
        Returns:
            Tuple[str, str]: A tuple containing the access token and refresh token
        """
        # Generate fingerprint from user agent if available
        fingerprint = None
        if user_agent:
            from app.core.security.fingerprint import generate_fingerprint
            # Create a fingerprint based on user agent
            # This helps prevent token reuse across different devices/browsers
            fingerprint = generate_fingerprint(user_agent)
        
        # Create tokens with fingerprint and IP address
        access_token = create_access_token(subject=user.id, fingerprint=fingerprint, ip_address=ip_address)
        refresh_token = create_refresh_token(subject=user.id, fingerprint=fingerprint, ip_address=ip_address)
        
        # Store refresh token in database if session is provided
        if db:
            expires_at = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            session = UserSession(
                user_id=user.id,
                refresh_token=refresh_token,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=expires_at,
                is_active=True
            )
            db.add(session)
            db.commit()
        
        return access_token, refresh_token
    
    @staticmethod
    def get_token_data(user: User, is_2fa_verified: bool = False) -> TokenData:
        """
        Get token data for a user.
        
        Args:
            user: The user to get token data for
            is_2fa_verified: Whether 2FA has been verified for this session
            
        Returns:
            TokenData: The token data
        """
        return TokenData(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_2fa_enabled=user.is_2fa_enabled,
            is_2fa_verified=is_2fa_verified
        )
    
    @staticmethod
    def setup_2fa(db: Session, user_id: int) -> Tuple[str, str]:
        """
        Set up 2FA for a user.
        
        Args:
            db: Database session
            user_id: ID of the user to set up 2FA for
            
        Returns:
            Tuple[str, str]: A tuple containing the TOTP secret and URI
        
        Raises:
            HTTPException: If user not found or 2FA already set up
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if 2FA is already set up
        if user.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA already set up"
            )
        
        # Generate TOTP secret
        secret = generate_totp_secret()
        
        # Create TOTP secret record
        totp_secret = TOTPSecret(
            user_id=user.id,
            secret=secret,
            is_verified=False
        )
        
        db.add(totp_secret)
        db.commit()
        
        # Generate TOTP URI for QR code
        from app.core.security.totp import get_totp_uri
        uri = get_totp_uri(secret, user.username)
        
        return secret, uri
    
    @staticmethod
    def verify_2fa_setup(db: Session, user_id: int, token: str) -> List[str]:
        """
        Verify 2FA setup with a TOTP token.
        
        Args:
            db: Database session
            user_id: ID of the user to verify 2FA setup for
            token: TOTP token to verify
            
        Returns:
            List[str]: List of backup codes
            
        Raises:
            HTTPException: If user not found, 2FA not set up, or token invalid
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or TOTP secret not found"
            )
        
        # Verify TOTP token
        if not verify_totp(user.totp_secret.secret, token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP token"
            )
        
        # Mark TOTP secret as verified
        user.totp_secret.is_verified = True
        user.is_2fa_enabled = True
        
        # Generate backup codes
        backup_codes_plain, backup_codes_hashed = generate_backup_codes()
        
        # Store backup codes
        for hashed_code in backup_codes_hashed:
            backup_code = BackupCode(
                user_id=user.id,
                hashed_code=hashed_code,
                is_used=False
            )
            db.add(backup_code)
        
        db.commit()
        
        return backup_codes_plain
    
    @staticmethod
    def verify_2fa(db: Session, user_id: int, token: str) -> bool:
        """
        Verify a 2FA token during login.
        
        Args:
            db: Database session
            user_id: ID of the user to verify 2FA for
            token: TOTP token or backup code to verify
            
        Returns:
            bool: True if verification succeeds, False otherwise
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.totp_secret or not user.is_2fa_enabled:
            return False
        
        # Try to verify as TOTP token
        if verify_totp(user.totp_secret.secret, token):
            return True
        
        # Try to verify as backup code
        backup_codes = db.query(BackupCode).filter(
            BackupCode.user_id == user_id,
            BackupCode.is_used == False
        ).all()
        
        for backup_code in backup_codes:
            if verify_password(token, backup_code.hashed_code):
                # Mark backup code as used
                backup_code.is_used = True
                db.commit()
                return True
        
        return False
    
    @staticmethod
    def disable_2fa(db: Session, user_id: int) -> bool:
        """
        Disable 2FA for a user.
        
        Args:
            db: Database session
            user_id: ID of the user to disable 2FA for
            
        Returns:
            bool: True if 2FA was disabled, False otherwise
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Delete TOTP secret
        if user.totp_secret:
            db.delete(user.totp_secret)
        
        # Delete backup codes
        for backup_code in user.backup_codes:
            db.delete(backup_code)
        
        user.is_2fa_enabled = False
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_sessions(db: Session, user_id: int, current_token: Optional[str] = None) -> List[UserSession]:
        """
        Get active sessions for a user.
        
        Args:
            db: Database session
            user_id: ID of the user to get sessions for
            current_token: Optional current refresh token to mark current session
            
        Returns:
            List[UserSession]: List of active sessions
        """
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).all()
        
        # Mark current session
        if current_token:
            for session in sessions:
                if session.refresh_token == current_token:
                    session.is_current = True
        
        return sessions
    
    @staticmethod
    def terminate_session(db: Session, session_id: int, user_id: int) -> bool:
        """
        Terminate a user session.
        
        Args:
            db: Database session
            session_id: ID of the session to terminate
            user_id: ID of the user who owns the session
            
        Returns:
            bool: True if session was terminated, False otherwise
        """
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == user_id
        ).first()
        
        if not session:
            return False
        
        session.is_active = False
        db.commit()
        
        return True
    
    @staticmethod
    def terminate_all_sessions(db: Session, user_id: int, except_token: Optional[str] = None) -> int:
        """
        Terminate all sessions for a user except the current one.
        
        Args:
            db: Database session
            user_id: ID of the user to terminate sessions for
            except_token: Optional token to exclude from termination
            
        Returns:
            int: Number of terminated sessions
        """
        query = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        )
        
        if except_token:
            query = query.filter(UserSession.refresh_token != except_token)
        
        sessions = query.all()
        count = len(sessions)
        
        for session in sessions:
            session.is_active = False
        
        db.commit()
        
        return count