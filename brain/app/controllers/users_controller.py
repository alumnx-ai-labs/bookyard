"""
Users and Ratings API controller.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select

from app.models import User, UserCreate, UserRating, UserRatingCreate
from app.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found"}}
)


# --- User Endpoints ---

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Create a new user.
    """
    # Check if user already exists if we're doing manual ID or unique username
    # For now, just simplistic create
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/users", response_model=List[User])
async def list_users(
    skip: int = 0, 
    limit: int = 10, 
    session: Session = Depends(get_session)
):
    """
    List all users.
    """
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    """
    Get generic user by ID.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# --- User Rating Endpoints ---

@router.post("/userratings", response_model=UserRating, status_code=status.HTTP_201_CREATED)
async def create_rating(rating: UserRatingCreate, session: Session = Depends(get_session)):
    """
    Create a new rating.
    """
    db_rating = UserRating.model_validate(rating)
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating


@router.get("/userratings", response_model=List[UserRating])
async def list_ratings(
    skip: int = 0, 
    limit: int = 10, 
    session: Session = Depends(get_session)
):
    """
    List all ratings.
    """
    statement = select(UserRating).offset(skip).limit(limit)
    ratings = session.exec(statement).all()
    return ratings
