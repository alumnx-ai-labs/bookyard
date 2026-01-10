"""
Books API controller with CRUD endpoints.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models import Book, BookCreate, BookUpdate
from app import database

logger = logging.getLogger(__name__)

# Create a router for books endpoints
router = APIRouter(
    prefix="/api/books",
    tags=["books"],
    responses={404: {"description": "Not found"}}
)


@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    """
    Create a new book.
    
    Args:
        book: BookCreate model with book details
        
    Returns:
        Book: Created book with ID
    """
    created_book = database.create_book(book)
    logger.info(f"Book created: {created_book.id} - {book.title}")
    return created_book


@router.get("", response_model=List[Book])
async def list_books(skip: int = 0, limit: int = 10):
    """
    List all books with pagination.
    
    Args:
        skip: Number of books to skip (default: 0)
        limit: Maximum number of books to return (default: 10)
        
    Returns:
        List[Book]: List of books
    """
    logger.info(f"Fetching books - skip: {skip}, limit: {limit}")
    books = database.get_all_books(skip=skip, limit=limit)
    return books


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int):
    """
    Get a specific book by ID.
    
    Args:
        book_id: ID of the book
        
    Returns:
        Book: Book details
        
    Raises:
        HTTPException: 404 if book not found
    """
    book = database.get_book_by_id(book_id)
    
    if not book:
        logger.warning(f"Book not found: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    return book


@router.put("/{book_id}", response_model=Book)
async def update_book(book_id: int, book_update: BookUpdate):
    """
    Update a specific book.
    
    Args:
        book_id: ID of the book
        book_update: Fields to update
        
    Returns:
        Book: Updated book details
        
    Raises:
        HTTPException: 404 if book not found
    """
    updated_book = database.update_book(book_id, book_update)
    
    if not updated_book:
        logger.warning(f"Book not found for update: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    logger.info(f"Book updated: {book_id}")
    return updated_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    """
    Delete a specific book.
    
    Args:
        book_id: ID of the book
        
    Raises:
        HTTPException: 404 if book not found
    """
    deleted = database.delete_book(book_id)
    
    if not deleted:
        logger.warning(f"Book not found for deletion: {book_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    logger.info(f"Book deleted: {book_id}")
    return None
