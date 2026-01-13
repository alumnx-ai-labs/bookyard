"""Books API endpoints."""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db.session import get_session  # Changed from get_db
from app.crud.crud_book import crud_book
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[BookResponse])
def list_books(
    db: Session = Depends(get_session),  # Changed
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by title or author")
):
    """List all books with pagination and search."""
    books = crud_book.get_multi_with_filters(db, skip=skip, limit=limit, search=search)
    total = crud_book.count_with_filters(db, search=search)
    
    return {"items": books, "total": total, "skip": skip, "limit": limit}


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_session)):  # Changed
    """Get a specific book by ID."""
    book = crud_book.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_session)  # Changed
):
    """Create a new book."""
    # Use a default owner_id for now
    default_owner_id = "00000000-0000-0000-0000-000000000000"
    book = crud_book.create(db, obj_in=book_in, owner_id=default_owner_id)
    logger.info(f"Book created: {book.id} - {book.title}")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_session)  # Changed
):
    """Update a book."""
    book = crud_book.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update timestamp
    book_in_dict = book_in.model_dump(exclude_unset=True)
    book_in_dict['updated_at'] = datetime.utcnow()
    
    updated_book = crud_book.update(db, db_obj=book, obj_in=book_in_dict)
    logger.info(f"Book updated: {book_id}")
    return updated_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_session)  # Changed
):
    """Delete a book."""
    book = crud_book.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    crud_book.delete(db, id=book_id)
    logger.info(f"Book deleted: {book_id}")
    return None