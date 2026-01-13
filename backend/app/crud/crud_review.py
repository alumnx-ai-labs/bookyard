"""CRUD operations for Review."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, func, and_

from app.crud.base import CRUDBase
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewStats


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    """CRUD operations for reviews."""
    
    def create_with_user_check(
        self, db: Session, *, obj_in: ReviewCreate
    ) -> Optional[Review]:
        """Create a review but check if it exists for user first."""
        existing_review = self.get_by_book_and_user(
            db, book_id=obj_in.book_id, user_id=obj_in.user_id
        )
        if existing_review:
            return None
        
        return self.create(db, obj_in=obj_in)

    def get_by_book_and_user(
        self, db: Session, *, book_id: int, user_id: UUID
    ) -> Optional[Review]:
        """Get a review by book and user."""
        statement = select(Review).where(
            and_(Review.book_id == book_id, Review.user_id == user_id)
        )
        return db.exec(statement).first()

    def get_multi_by_book(
        self, db: Session, *, book_id: int, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        """Get reviews for a specific book."""
        statement = select(Review).where(Review.book_id == book_id)\
            .offset(skip).limit(limit)
        return db.exec(statement).all()
        
    def count_by_book(self, db: Session, *, book_id: int) -> int:
        """Count reviews for a book."""
        statement = select(func.count()).select_from(Review).where(Review.book_id == book_id)
        return db.exec(statement).one()

    def get_stats_by_book(self, db: Session, *, book_id: int) -> ReviewStats:
        """Get review statistics for a book."""
        # Calculate average rating
        avg_stm = select(func.avg(Review.rating)).where(Review.book_id == book_id)
        avg_rating = db.exec(avg_stm).one()
        
        # Calculate count
        count_stm = select(func.count()).select_from(Review).where(Review.book_id == book_id)
        count = db.exec(count_stm).one()
        
        return ReviewStats(
            average_rating=float(avg_rating) if avg_rating else 0.0,
            review_count=count
        )


crud_review = CRUDReview(Review)
