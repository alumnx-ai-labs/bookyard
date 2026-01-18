"""User and Rating database models."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model."""
    username: Optional[str] = Field(default=None, max_length=100, index=True)
    location: Optional[str] = Field(default=None, max_length=255)
    age: Optional[int] = Field(default=None)


class User(UserBase, table=True):
    """Database model for Users."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRatingBase(SQLModel):
    """Base rating model."""
    rating: int = Field(ge=0, le=10)
    user_id: int = Field(foreign_key="user.id", index=True)
    book_isbn: str = Field(index=True)


class UserRating(UserRatingBase, table=True):
    """Database model for User Ratings."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
