"""
Pydantic and SQLModel models for the Bookyard API.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


# --- Shared Models (Pydantic/SQLModel Base) ---

class HealthResponse(SQLModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str


class Message(SQLModel):
    """Generic message response model."""
    message: str


# --- Book Models ---

class BookBase(SQLModel):
    """Base book model with common fields."""
    title: str = Field(min_length=1, max_length=200, index=True)
    author: str = Field(min_length=1, max_length=100, index=True)
    isbn: Optional[str] = Field(default=None, max_length=20, index=True, unique=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    published_year: Optional[int] = Field(default=None, ge=1000, le=2100)
    pages: Optional[int] = Field(default=None, ge=1)
    # Image URLs from dataset
    image_url_s: Optional[str] = Field(default=None)
    image_url_m: Optional[str] = Field(default=None)
    image_url_l: Optional[str] = Field(default=None)


class Book(BookBase, table=True):
    """Database model for Books."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BookCreate(BookBase):
    """Model for creating a new book."""
    pass


class BookUpdate(SQLModel):
    """Model for updating a book."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = Field(default=None, max_length=1000)
    published_year: Optional[int] = Field(default=None, ge=1000, le=2100)
    pages: Optional[int] = Field(default=None, ge=1)
    image_url_s: Optional[str] = Field(default=None)
    image_url_m: Optional[str] = Field(default=None)
    image_url_l: Optional[str] = Field(default=None)


# --- User Models ---

class UserBase(SQLModel):
    """Base user model."""
    username: Optional[str] = Field(default=None, max_length=100, index=True)
    # User-ID from dataset seems to be integer, but let's support string if needed properly.
    # Looking at typical Book-Crossing dataset, User-ID is int.
    # We will map dataset 'User-ID' to 'external_id' or 'id' if we want.
    # Let's assume for now we generate our own IDs and store dataset ID as well if needed.
    # But often for bulk load effectively we want to keep the IDs if possible?
    # Let's stick effectively to mapped schema.
    
    # Dataset fields: User-ID, Location, Age
    location: Optional[str] = Field(default=None, max_length=255)
    age: Optional[int] = Field(default=None)


class User(UserBase, table=True):
    """Database model for Users."""
    id: Optional[int] = Field(default=None, primary_key=True)  # This will map to User-ID from dataset
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    """Model for creating a user."""
    id: Optional[int] = Field(default=None) # Allow specifying ID for bulk load


# --- Rating Models ---

class UserRatingBase(SQLModel):
    """Base rating model."""
    rating: int = Field(ge=0, le=10) # 0-10 scale in dataset
    user_id: int = Field(foreign_key="user.id", index=True)
    # Dataset links "ISBN" to rating, not Book ID. 
    # Ideally standard SQL links to Book ID. 
    # We should probably store ISBN here too to match dataset easily, OR query book ID.
    # Given the dataset structure (Books.csv has ISBN), it's safer to link via ISBN if we want raw speed, 
    # OR we make Book.isbn unique and link via text key? 
    # Efficient way: Store ISBN as foreign key or just string reference for now 
    # IF we change Book Primary Key to ISBN? No, int ID is better.
    # We will store `book_isbn` as the link for this specific dataset structure.
    book_isbn: str = Field(index=True)


class UserRating(UserRatingBase, table=True):
    """Database model for User Ratings."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRatingCreate(UserRatingBase):
    """Model for creating a rating."""
    pass
