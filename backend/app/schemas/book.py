"""Book Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class BookBase(BaseModel):
    """Base book schema."""
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    pages: Optional[int] = Field(None, ge=1)


class BookCreate(BookBase):
    """Schema for creating a book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    pages: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class BookResponse(BookBase):
    """Schema for book response."""
    id: int
    owner_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
