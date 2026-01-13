"""Books API endpoints."""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.memory import get_memory_session, books_db, MemoryBook
from app.api.endpoints.deps import get_user_id_from_token
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=PaginatedResponse[BookResponse])
def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by title or author")
):
    """List all books with pagination and search."""
    books = [BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description,
        published_year=book.published_year,
        pages=book.pages,
        owner_id=book.owner_id,
        is_active=book.is_active,
        created_at=book.created_at,
        updated_at=book.updated_at
    ) for book in books_db[skip:skip+limit]]
    
    return {"items": books, "total": len(books_db), "skip": skip, "limit": limit}


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    """Get a specific book by ID."""
    book = next((b for b in books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description,
        published_year=book.published_year,
        pages=book.pages,
        owner_id=book.owner_id,
        is_active=book.is_active,
        created_at=book.created_at,
        updated_at=book.updated_at
    )


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    current_user_id: str = Depends(get_user_id_from_token)
):
    """Create a new book."""
    book = MemoryBook(
        title=book_in.title,
        author=book_in.author,
        isbn=book_in.isbn,
        description=book_in.description,
        published_year=book_in.published_year,
        pages=book_in.pages,
        owner_id=current_user_id
    )
    books_db.append(book)
    
    logger.info(f"Book created: {book.id} - {book.title} by {current_user_id}")
    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description,
        published_year=book.published_year,
        pages=book.pages,
        owner_id=book.owner_id,
        is_active=book.is_active,
        created_at=book.created_at,
        updated_at=book.updated_at
    )


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_in: BookUpdate
):
    """Update a book."""
    book = next((b for b in books_db if b.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update fields
    if book_in.title is not None:
        book.title = book_in.title
    if book_in.author is not None:
        book.author = book_in.author
    if book_in.isbn is not None:
        book.isbn = book_in.isbn
    if book_in.description is not None:
        book.description = book_in.description
    if book_in.published_year is not None:
        book.published_year = book_in.published_year
    if book_in.pages is not None:
        book.pages = book_in.pages
    
    book.updated_at = datetime.utcnow()
    
    logger.info(f"Book updated: {book_id}")
    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description,
        published_year=book.published_year,
        pages=book.pages,
        owner_id=book.owner_id,
        is_active=book.is_active,
        created_at=book.created_at,
        updated_at=book.updated_at
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    """Delete a book."""
    book_index = next((i for i, b in enumerate(books_db) if b.id == book_id), None)
    if book_index is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    books_db.pop(book_index)
    logger.info(f"Book deleted: {book_id}")
    return None