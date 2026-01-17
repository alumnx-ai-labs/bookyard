"""Review schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    """Base review schema."""
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = Field(default=None, max_length=1000)


class ReviewCreateRequest(ReviewBase):
    """Review creation request schema (from user)."""
    book_id: int


class ReviewCreate(ReviewCreateRequest):
    """Review creation schema (internal)."""
    user_id: UUID


class ReviewUpdate(ReviewBase):
    """Review update schema."""
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    # text is already optional in Base, but we need to allow partial updates so strict re-definition might be needed 
    # or just inherit and make fields optional. 
    # Let's redefine for clarity in Update.
    text: Optional[str] = None


class ReviewResponse(ReviewBase):
    """Review response schema."""
    id: int
    book_id: int
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewStats(BaseModel):
    """Review statistics schema."""
    average_rating: float
    review_count: int
