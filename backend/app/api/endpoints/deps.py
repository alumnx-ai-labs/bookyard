"""Common API dependencies."""

from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.session import get_session


def get_db():
    """Get database session."""
    return get_session()


def get_user_id_from_token(current_user: dict = Depends(get_current_user)) -> UUID:
    """Extract user ID from JWT token."""
    try:
        return UUID(current_user["sub"])
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )