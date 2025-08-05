from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.auth.auth import get_current_user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current user and verify that they are active.
    
    Args:
        current_user: The current user
        
    Returns:
        User: The current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user