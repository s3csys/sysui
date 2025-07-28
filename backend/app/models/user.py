from sqlalchemy import Boolean, Column, String, Enum, Text, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
from typing import List, Optional, Set, ClassVar, TYPE_CHECKING, ForwardRef
from datetime import datetime

from app.models.base import Base

# Import the association table directly to avoid circular imports
from app.models.user_permission import user_permission_association

# Use TYPE_CHECKING for type hints to avoid circular imports
if TYPE_CHECKING:
    from app.models.user_permission import UserPermission


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
    
    __allow_unmapped__ = True  # Allow legacy annotations to be used alongside Mapped
    
    # Basic user information
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Authentication fields
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Authorization fields
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    # Custom permissions (many-to-many relationship)
    # This is a collection of permission strings from the Permission enum
    custom_permissions: Mapped[Set[str]] = relationship(
        secondary=user_permission_association,
        collection_class=set,
        lazy="joined",
        cascade="save-update, merge, refresh-expire, expunge",
        uselist=True
    )
    
    # 2FA fields
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    
    # Relationships
    totp_secret: Mapped[Optional["TOTPSecret"]] = relationship(
        "TOTPSecret", 
        back_populates="user", 
        uselist=False, 
        cascade="all, delete-orphan",
        lazy="joined"
    )
    backup_codes: Mapped[List["BackupCode"]] = relationship(
        "BackupCode", 
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    sessions: Mapped[List["Session"]] = relationship(
        "Session", 
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
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
    
    __allow_unmapped__ = True  # Allow legacy annotations to be used alongside Mapped
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    secret: Mapped[str] = mapped_column(String(50), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="totp_secret", foreign_keys=[user_id])
    
    def __repr__(self) -> str:
        return f"<TOTPSecret user_id={self.user_id}>"


class BackupCode(Base):
    """Backup codes for 2FA recovery"""
    
    __allow_unmapped__ = True  # Allow legacy annotations to be used alongside Mapped
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    hashed_code: Mapped[str] = mapped_column(String(100), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="backup_codes", foreign_keys=[user_id])
    
    def __repr__(self) -> str:
        return f"<BackupCode user_id={self.user_id} is_used={self.is_used}>"


class Session(Base):
    """User session for tracking active logins"""
    
    __allow_unmapped__ = True  # Allow legacy annotations to be used alongside Mapped
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions", foreign_keys=[user_id])
    
    def __repr__(self) -> str:
        return f"<Session user_id={self.user_id} is_active={self.is_active}>"