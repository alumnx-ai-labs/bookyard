"""Database base - imports all models for migrations."""

from sqlmodel import SQLModel

from app.models.book import Book

__all__ = ["SQLModel", "Book"]