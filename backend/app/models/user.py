from sqlalchemy import Boolean, Column, String, Enum, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
import enum
from typing import List, Optional, Set
from datetime import datetime

from app.models.base import Base
from app.models.user_permission import user_permission_association


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    
    # Method to check if a role has higher or equal privileges than another role
    @classmethod
    def has_permission(cls, user_role: 'UserRole', required_role: 'UserRole') -> bool:
        """Check if a user role has sufficient permissions for a required role.
        
        Args:
            user_role: The user's role
            required_role: The required role for an operation
            
        Returns:
            bool: True if the user role has sufficient permissions, False otherwise
        """
        # Role hierarchy: ADMIN > EDITOR > VIEWER
        role_hierarchy = {
            cls.ADMIN: 3,
            cls.EDITOR: 2,
            cls.VIEWER: 1
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


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
    
    # Custom permissions (many-to-many relationship)
    custom_permissions = relationship(
        "permission",
        secondary=user_permission_association,
        collection_class=set
    )
    
    # 2FA fields
    is_2fa_enabled = Column(Boolean(), default=False, nullable=False)
    
    # Relationships
    totp_secret = relationship("TOTPSecret", back_populates="user", uselist=False, cascade="all, delete-orphan")
    backup_codes = relationship("BackupCode", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def has_permission(self, permission: str) -> bool:
        """Check if the user has a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            bool: True if the user has the permission, False otherwise
        """
        from app.models.user_permission import UserPermission
        return UserPermission.has_permission(self, permission)
    
    def get_permissions(self) -> Set[str]:
        """Get all permissions for the user.
        
        Returns:
            Set[str]: A set of all permission names for the user
        """
        from app.models.user_permission import UserPermission
        return UserPermission.get_user_permissions(self)
    
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