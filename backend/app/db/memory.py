"""In-memory database for development."""

from typing import List, Optional
from datetime import datetime
from uuid import UUID

# In-memory storage
books_db = []
reviews_db = []
next_book_id = 1
next_review_id = 1

class MemoryBook:
    def __init__(self, **kwargs):
        global next_book_id
        self.id = next_book_id
        next_book_id += 1
        self.title = kwargs.get('title')
        self.author = kwargs.get('author')
        self.isbn = kwargs.get('isbn')
        self.description = kwargs.get('description')
        self.published_year = kwargs.get('published_year')
        self.pages = kwargs.get('pages')
        self.owner_id = kwargs.get('owner_id')
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class MemoryReview:
    def __init__(self, **kwargs):
        global next_review_id
        self.id = next_review_id
        next_review_id += 1
        self.book_id = kwargs.get('book_id')
        self.user_id = kwargs.get('user_id')
        self.rating = kwargs.get('rating')
        self.text = kwargs.get('text')
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

def get_memory_session():
    """Mock session for in-memory database."""
    return None