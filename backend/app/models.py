"""
Pydantic models for the Bookyard API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str


class Message(BaseModel):
    """Generic message response model."""
    message: str


class BookBase(BaseModel):
    """Base book model with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    pages: Optional[int] = Field(None, ge=1)


class BookCreate(BookBase):
    """Model for creating a new book."""
    pass


class BookUpdate(BaseModel):
    """Model for updating a book."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=1000)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    pages: Optional[int] = Field(None, ge=1)


class Book(BookBase):
    """Complete book model with ID."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True
