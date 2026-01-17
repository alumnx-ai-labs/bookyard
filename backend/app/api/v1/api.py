"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import books, reviews

api_router = APIRouter()

api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])