"""Reviews API endpoints."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db.memory import get_memory_session, reviews_db, MemoryReview
from app.api.endpoints.deps import get_user_id_from_token
from app.schemas.review import ReviewCreate, ReviewCreateRequest, ReviewResponse, ReviewStats
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreateRequest,
    current_user_id: UUID = Depends(get_user_id_from_token)
):
    """
    Create a new review.
    
    Enforces one review per user per book.
    """
    # Check if review already exists
    existing = next((r for r in reviews_db if r.book_id == review_in.book_id and str(r.user_id) == str(current_user_id)), None)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="User has already reviewed this book"
        )
    
    # Create review
    review = MemoryReview(
        book_id=review_in.book_id,
        user_id=current_user_id,
        rating=review_in.rating,
        text=review_in.text
    )
    reviews_db.append(review)
    
    logger.info(f"Review created for book {review_in.book_id} by user {current_user_id}")
    return ReviewResponse(
        id=review.id,
        book_id=review.book_id,
        user_id=review.user_id,
        rating=review.rating,
        text=review.text,
        created_at=review.created_at,
        updated_at=review.updated_at
    )


@router.get("/", response_model=PaginatedResponse[ReviewResponse])
def list_reviews(
    book_id: int = Query(..., description="Filter by book ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List reviews for a book.
    """
    book_reviews = [r for r in reviews_db if r.book_id == book_id]
    paginated_reviews = book_reviews[skip:skip+limit]
    
    reviews = [ReviewResponse(
        id=review.id,
        book_id=review.book_id,
        user_id=review.user_id,
        rating=review.rating,
        text=review.text,
        created_at=review.created_at,
        updated_at=review.updated_at
    ) for review in paginated_reviews]
    
    return {"items": reviews, "total": len(book_reviews), "skip": skip, "limit": limit}


@router.get("/stats", response_model=ReviewStats)
def get_review_stats(
    book_id: int = Query(..., description="Book ID")
):
    """Get review statistics (average rating, count) for a book."""
    book_reviews = [r for r in reviews_db if r.book_id == book_id]
    
    if not book_reviews:
        return ReviewStats(average_rating=0.0, review_count=0)
    
    total_rating = sum(r.rating for r in book_reviews)
    average_rating = total_rating / len(book_reviews)
    
    return ReviewStats(average_rating=average_rating, review_count=len(book_reviews))
