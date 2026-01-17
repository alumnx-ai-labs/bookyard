"""Database base - imports all models for migrations."""

from sqlmodel import SQLModel

from app.models.book import Book
from app.models.review import Review

__all__ = ["SQLModel", "Book", "Review"]