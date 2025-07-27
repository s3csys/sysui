import logging
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize the database with initial data"""
    # Create admin user if it doesn't exist
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        logger.info("Creating admin user")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),  # This should be changed immediately
            is_active=True,
            is_verified=True,
            role=UserRole.ADMIN,
        )
        db.add(admin_user)
        db.commit()
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists")