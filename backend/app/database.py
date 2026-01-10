"""
In-memory database storage for development.
"""

from datetime import datetime
from typing import Dict, List, Optional
from app.models import Book, BookCreate, BookUpdate

# In-memory database
books_db: Dict[int, dict] = {}
next_book_id = 1


def create_book(book: BookCreate) -> Book:
    """
    Create a new book in the database.
    
    Args:
        book: BookCreate model with book details
        
    Returns:
        Book: Created book with ID and timestamps
    """
    global next_book_id
    
    book_id = next_book_id
    next_book_id += 1
    
    now = datetime.utcnow()
    new_book = {
        "id": book_id,
        **book.dict(),
        "created_at": now,
        "updated_at": now
    }
    
    books_db[book_id] = new_book
    return Book(**new_book)


def get_all_books(skip: int = 0, limit: int = 10) -> List[Book]:
    """
    Get all books with pagination.
    
    Args:
        skip: Number of books to skip
        limit: Maximum number of books to return
        
    Returns:
        List[Book]: List of books
    """
    books = list(books_db.values())
    return [Book(**book) for book in books[skip : skip + limit]]


def get_book_by_id(book_id: int) -> Optional[Book]:
    """
    Get a specific book by ID.
    
    Args:
        book_id: ID of the book
        
    Returns:
        Book: Book details or None if not found
    """
    if book_id in books_db:
        return Book(**books_db[book_id])
    return None


def update_book(book_id: int, book_update: BookUpdate) -> Optional[Book]:
    """
    Update a specific book.
    
    Args:
        book_id: ID of the book
        book_update: Fields to update
        
    Returns:
        Book: Updated book or None if not found
    """
    if book_id not in books_db:
        return None
    
    book = books_db[book_id]
    update_data = book_update.dict(exclude_unset=True)
    
    updated_book = {**book, **update_data, "updated_at": datetime.utcnow()}
    books_db[book_id] = updated_book
    
    return Book(**updated_book)


def delete_book(book_id: int) -> bool:
    """
    Delete a specific book.
    
    Args:
        book_id: ID of the book
        
    Returns:
        bool: True if deleted, False if not found
    """
    if book_id in books_db:
        del books_db[book_id]
        return True
    return False


def book_exists(book_id: int) -> bool:
    """
    Check if a book exists.
    
    Args:
        book_id: ID of the book
        
    Returns:
        bool: True if book exists, False otherwise
    """
    return book_id in books_db
