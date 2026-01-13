"""Book database model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class Book(SQLModel, table=True):
    """Book model for database."""
    
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    author: str = Field(max_length=100, index=True)
    isbn: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = Field(default=None, max_length=1000)
    published_year: Optional[int] = Field(default=None)
    pages: Optional[int] = Field(default=None)
    
    # Owner field - optional for now
    owner_id: Optional[UUID] = Field(default=None, index=True)
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)