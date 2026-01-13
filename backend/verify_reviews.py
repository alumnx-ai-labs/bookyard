"""Verification script for Reviews feature."""

import os
import sys

# Set SQLite DB for testing
os.environ["DATABASE_URL"] = "sqlite://"

# Add current directory to path
sys.path.append(os.getcwd())

from sqlmodel import Session, SQLModel, create_engine
from app.models.book import Book
from app.models.review import Review
from app.crud.crud_review import crud_review
from app.api.v1.endpoints.reviews import create_review, list_reviews, get_review_stats
from app.schemas.review import ReviewCreate

# Re-create engine for SQLite
from app.db import session as db_session
db_session.engine = create_engine("sqlite://", echo=False, connect_args={"check_same_thread": False})
engine = db_session.engine

def setup_db():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)

def verify_reviews():
    setup_db()
    
    with Session(engine) as db:
        print("Creating test book...")
        book = Book(title="Test Book", author="Test Author")
        db.add(book)
        db.commit()
        db.refresh(book)
        
        user1_id = "11111111-1111-1111-1111-111111111111"
        user2_id = "22222222-2222-2222-2222-222222222222"
        
        print(f"Book ID: {book.id}")
        
        # 1. Create Review (User 1)
        print("\n1. Testing Create Review (User 1)...")
        review_in = ReviewCreate(
            book_id=book.id,
            user_id=user1_id,
            rating=5,
            text="Great book!"
        )
        review1 = crud_review.create_with_user_check(db, obj_in=review_in)
        assert review1 is not None
        assert review1.rating == 5
        print("✓ Review created successfully")
        
        # 2. Duplicate Review Check
        print("\n2. Testing Duplicate Review Constraint...")
        dup_review = crud_review.create_with_user_check(db, obj_in=review_in)
        assert dup_review is None
        print("✓ Duplicate review prevented")
        
        # 3. Create Review (User 2)
        print("\n3. Testing Create Review (User 2)...")
        review2_in = ReviewCreate(
            book_id=book.id,
            user_id=user2_id,
            rating=3,
            text="Average book."
        )
        review2 = crud_review.create_with_user_check(db, obj_in=review2_in)
        assert review2 is not None
        print("✓ Second review created successfully")
        
        # 4. Check Stats
        print("\n4. Testing Stats Calculation...")
        stats = crud_review.get_stats_by_book(db, book_id=book.id)
        print(f"Stats: Avg={stats.average_rating}, Count={stats.review_count}")
        assert stats.review_count == 2
        assert stats.average_rating == 4.0  # (5+3)/2
        print("✓ Stats calculated correctly")
        
        # 5. List Reviews
        print("\n5. Testing List Reviews...")
        reviews = crud_review.get_multi_by_book(db, book_id=book.id)
        assert len(reviews) == 2
        print("✓ Reviews listed correctly")
        
    print("\n✓ ALL TESTS PASSED")

if __name__ == "__main__":
    verify_reviews()
