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
from app.models.user import User
from app.services.auth.auth_service import AuthService


async def create_admin_user():
    """Create a default admin user if no admin exists."""
    async for db in get_db():
        # Check if admin user already exists
        admin = await db.query(User).filter(User.role == "admin").first()
        if admin:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")
        
        try:
            # Create user with admin role
            user = await AuthService.create_user(
                db=db,
                username=admin_username,
                email=admin_email,
                password=admin_password,
                full_name="System Administrator",
                role="admin"
            )
            
            # Verify the admin user automatically
            if user and user.verification_token:
                await AuthService.verify_email(db=db, token=user.verification_token)
                print(f"Admin user created and verified: {admin_username}")
            else:
                print("Failed to create admin user.")
        except Exception as e:
            print(f"Error creating admin user: {e}")


async def init_db():
    """Initialize the database with required data."""
    print("Initializing database...")
    await create_admin_user()
    print("Database initialization completed.")


if __name__ == "__main__":
    asyncio.run(init_db())