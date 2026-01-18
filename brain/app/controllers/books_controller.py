"""
Books API controller with CRUD endpoints.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from app.models import Book, BookCreate, BookUpdate
from app.database import get_session

logger = logging.getLogger(__name__)

# Create a router for books endpoints
router = APIRouter(
    prefix="/api/books",
    tags=["books"],
    responses={404: {"description": "Not found"}}
)


@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """
    Create a new book.
    """
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    logger.info(f"Book created: {db_book.id} - {db_book.title}")
    return db_book


@router.get("", response_model=List[Book])
async def list_books(
    skip: int = 0, 
    limit: int = 10, 
    session: Session = Depends(get_session)
):
    """
    List all books with pagination.
    """
    logger.info(f"Fetching books - skip: {skip}, limit: {limit}")
    statement = select(Book).offset(skip).limit(limit)
    books = session.exec(statement).all()
    return books


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int, session: Session = Depends(get_session)):
    """
    Get a specific book by ID.
    """
    book = session.get(Book, book_id)
    
    if not book:
        logger.warning(f"Book not found: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    return book


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int, 
    book_update: BookUpdate, 
    session: Session = Depends(get_session)
):
    """
    Update a specific book.
    """
    book = session.get(Book, book_id)
    
    if not book:
        logger.warning(f"Book not found for update: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
        
    book.updated_at = datetime.utcnow()

    session.add(book)
    session.commit()
    session.refresh(book)
    
    logger.info(f"Book updated: {book_id}")
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: Session = Depends(get_session)):
    """
    Delete a specific book.
    """
    book = session.get(Book, book_id)
    
    if not book:
        logger.warning(f"Book not found for deletion: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    session.delete(book)
    session.commit()
    
    logger.info(f"Book deleted: {book_id}")
    return None
