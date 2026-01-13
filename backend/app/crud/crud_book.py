"""CRUD operations for Book."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, or_

from app.crud.base import CRUDBase
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    """CRUD operations for books."""
    
    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        owner_id: Optional[UUID] = None
    ) -> List[Book]:
        """Get books with filters."""
        statement = select(Book)
        
        if owner_id is not None:
            statement = statement.where(Book.owner_id == owner_id)
        
        if search:
            search_filter = or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
            statement = statement.where(search_filter)
        
        statement = statement.offset(skip).limit(limit)
        results = db.exec(statement)
        return results.all()
    
    def count_with_filters(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        owner_id: Optional[UUID] = None
    ) -> int:
        """Count books with filters."""
        statement = select(Book)
        
        if owner_id is not None:
            statement = statement.where(Book.owner_id == owner_id)
        
        if search:
            search_filter = or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
            statement = statement.where(search_filter)
        
        results = db.exec(statement)
        return len(results.all())


crud_book = CRUDBook(Book)