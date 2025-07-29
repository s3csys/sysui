#!/usr/bin/env python
"""
Database initialization script.
Creates a default admin user if one doesn't exist.

Usage:
    python -m scripts.init_db
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.auth.auth_service import AuthService


def create_admin_user():
    """Create a default admin user if no admin exists."""
    db = next(get_db())
    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if admin:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")
        
        try:
            # Create user
            user = AuthService.create_user(
                db=db,
                username=admin_username,
                email=admin_email,
                password=admin_password,
                full_name="System Administrator"
            )
            
            # Set admin role
            if user:
                user.role = UserRole.ADMIN
                db.commit()
                
                # Verify the admin user automatically
                if user.verification_token:
                    AuthService.verify_email(db=db, token=user.verification_token)
                    print(f"Admin user created and verified: {admin_username}")
                else:
                    print("Failed to verify admin user.")
            else:
                print("Failed to create admin user.")
        except Exception as e:
            db.rollback()
            print(f"Error creating admin user: {e}")
    finally:
        db.close()


def init_db():
    """Initialize the database with required data."""
    print("Initializing database...")
    
    # Create all tables in the database
    from app.models.base import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # Initialize permissions
    init_permissions()
    
    # Create default admin user
    create_admin_user()
    
    print("Database initialization completed.")


def init_permissions():
    """Initialize the permissions table with all available permissions."""
    from app.models.permission import Permission, PermissionEnum
    
    db = next(get_db())
    try:
        # Check if permissions already exist
        existing_permissions = db.query(Permission).count()
        if existing_permissions > 0:
            print(f"Permissions already initialized ({existing_permissions} found).")
            return
            
        # Create all permissions from the PermissionEnum
        for permission in PermissionEnum:
            db.add(Permission(name=permission.value))
        
        db.commit()
        print(f"Initialized {len(PermissionEnum)} permissions.")
    except Exception as e:
        db.rollback()
        print(f"Error initializing permissions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()