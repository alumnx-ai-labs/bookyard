"""Review database model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel, UniqueConstraint


class Review(SQLModel, table=True):
    """Review model for database."""
    
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("book_id", "user_id", name="unique_user_book_review"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(index=True)  # Foreign key logic could be added but loose coupling for now is fine or proper FK: foreign_key="books.id"
    # To be safe and enable potential future relationships, let's use foreign_key if possible, 
    # but based on the plan, I'll stick to simple fields unless I edit Book model too. 
    # Actually, proper Foreign Keys are good practice.
    # book_id: int = Field(foreign_key="books.id", index=True) 
    # Since I haven't modified Book to have "back_populates", I will just use simple int for now to avoid issues if I don't migrate properly, 
    # BUT typically SQLModel wants the table to exist. "books" table exists.
    # Let's stick to what I planned: "book_id: int (FK to books)".
    # I'll add foreign_key="books.id" to be precise.
    
    book_id: int = Field(foreign_key="books.id", index=True)
    user_id: UUID = Field(index=True)
    rating: int = Field(ge=1, le=5)
    text: Optional[str] = Field(default=None, max_length=1000)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
