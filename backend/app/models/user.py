from sqlalchemy import Boolean, Column, String, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
import enum
from typing import List, Optional

from app.models.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization"""
    
    # Basic user information
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # Authentication fields
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_verified = Column(Boolean(), default=False, nullable=False)
    verification_token = Column(String(100), nullable=True)
    
    # Authorization fields
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    # 2FA fields
    is_2fa_enabled = Column(Boolean(), default=False, nullable=False)
    
    # Relationships
    totp_secret = relationship("TOTPSecret", back_populates="user", uselist=False, cascade="all, delete-orphan")
    backup_codes = relationship("BackupCode", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"


class TOTPSecret(Base):
    """TOTP secret for 2FA"""
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    secret = Column(String(50), nullable=False)
    is_verified = Column(Boolean(), default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="totp_secret")
    
    def __repr__(self) -> str:
        return f"<TOTPSecret user_id={self.user_id}>"


class BackupCode(Base):
    """Backup codes for 2FA recovery"""
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    hashed_code = Column(String(100), nullable=False)
    is_used = Column(Boolean(), default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="backup_codes")
    
    def __repr__(self) -> str:
        return f"<BackupCode user_id={self.user_id} is_used={self.is_used}>"


class Session(Base):
    """User session for tracking active logins"""
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(255), nullable=False, unique=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<Session user_id={self.user_id} is_active={self.is_active}>"