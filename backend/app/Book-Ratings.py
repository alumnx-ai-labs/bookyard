from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI(title="Book Ratings API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to CSV file
CSV_PATH = Path(__file__).parent / "data" / "Book-Ratings.csv"

# Load data on startup
ratings_df = None

@app.on_event("startup")
async def load_data():
    global ratings_df
    try:
        ratings_df = pd.read_csv(CSV_PATH, sep=';', encoding='latin-1', on_bad_lines='skip')
        # Clean column names - remove quotes and spaces
        ratings_df.columns = ratings_df.columns.str.replace('"', '').str.strip()
        print(f"Loaded {len(ratings_df)} ratings")
        print(f"Columns: {list(ratings_df.columns)}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        # Create empty dataframe with expected columns
        ratings_df = pd.DataFrame(columns=['User-ID', 'ISBN', 'Book-Rating'])

# Pydantic models
class Rating(BaseModel):
    user_id: int = Field(..., alias="User-ID")
    isbn: str = Field(..., alias="ISBN")
    rating: int = Field(..., alias="Book-Rating", ge=0, le=10)

    class Config:
        populate_by_name = True

class RatingCreate(BaseModel):
    user_id: int
    isbn: str
    rating: int = Field(..., ge=0, le=10)

class RatingStats(BaseModel):
    isbn: str
    average_rating: float
    total_ratings: int
    rating_distribution: dict

class UserStats(BaseModel):
    user_id: int
    total_ratings: int
    average_rating: float
    books_rated: List[str]

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Book Ratings API",
        "version": "1.0.0",
        "total_ratings": len(ratings_df) if ratings_df is not None else 0
    }

# Get all ratings with pagination
@app.get("/ratings", response_model=List[Rating])
async def get_ratings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all ratings with pagination"""
    if ratings_df is None or ratings_df.empty:
        return []
    
    start = skip
    end = skip + limit
    data = ratings_df.iloc[start:end].to_dict('records')
    return data

# Get rating by user and ISBN
@app.get("/ratings/{user_id}/{isbn}")
async def get_rating(user_id: int, isbn: str):
    """Get a specific rating by user ID and ISBN"""
    if ratings_df is None or ratings_df.empty:
        raise HTTPException(status_code=404, detail="No ratings data available")
    
    rating = ratings_df[
        (ratings_df['User-ID'] == user_id) & 
        (ratings_df['ISBN'] == isbn)
    ]
    
    if rating.empty:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    return rating.iloc[0].to_dict()

# Get ratings by user
@app.get("/users/{user_id}/ratings")
async def get_user_ratings(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all ratings by a specific user"""
    if ratings_df is None or ratings_df.empty:
        return []
    
    user_ratings = ratings_df[ratings_df['User-ID'] == user_id]
    
    if user_ratings.empty:
        raise HTTPException(status_code=404, detail="User not found or has no ratings")
    
    start = skip
    end = skip + limit
    return user_ratings.iloc[start:end].to_dict('records')

# Get user statistics
@app.get("/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: int):
    """Get statistics for a specific user"""
    if ratings_df is None or ratings_df.empty:
        raise HTTPException(status_code=404, detail="No ratings data available")
    
    user_ratings = ratings_df[ratings_df['User-ID'] == user_id]
    
    if user_ratings.empty:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "total_ratings": len(user_ratings),
        "average_rating": float(user_ratings['Book-Rating'].mean()),
        "books_rated": user_ratings['ISBN'].tolist()
    }

# Get ratings by book (ISBN)
@app.get("/books/{isbn}/ratings")
async def get_book_ratings(
    isbn: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all ratings for a specific book"""
    if ratings_df is None or ratings_df.empty:
        return []
    
    book_ratings = ratings_df[ratings_df['ISBN'] == isbn]
    
    if book_ratings.empty:
        raise HTTPException(status_code=404, detail="Book not found or has no ratings")
    
    start = skip
    end = skip + limit
    return book_ratings.iloc[start:end].to_dict('records')

# Get book statistics
@app.get("/books/{isbn}/stats", response_model=RatingStats)
async def get_book_stats(isbn: str):
    """Get statistics for a specific book"""
    if ratings_df is None or ratings_df.empty:
        raise HTTPException(status_code=404, detail="No ratings data available")
    
    book_ratings = ratings_df[ratings_df['ISBN'] == isbn]
    
    if book_ratings.empty:
        raise HTTPException(status_code=404, detail="Book not found")
    
    ratings_count = book_ratings['Book-Rating'].value_counts().to_dict()
    
    return {
        "isbn": isbn,
        "average_rating": float(book_ratings['Book-Rating'].mean()),
        "total_ratings": len(book_ratings),
        "rating_distribution": {str(k): int(v) for k, v in ratings_count.items()}
    }

# Get top rated books
@app.get("/books/top-rated")
async def get_top_rated_books(
    min_ratings: int = Query(10, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """Get top rated books with minimum number of ratings"""
    if ratings_df is None or ratings_df.empty:
        return []
    
    # Group by ISBN and calculate stats
    book_stats = ratings_df.groupby('ISBN').agg({
        'Book-Rating': ['mean', 'count']
    }).reset_index()
    
    book_stats.columns = ['ISBN', 'average_rating', 'total_ratings']
    
    # Filter by minimum ratings and sort
    top_books = book_stats[book_stats['total_ratings'] >= min_ratings]
    top_books = top_books.sort_values('average_rating', ascending=False).head(limit)
    
    return top_books.to_dict('records')

# Get most active users
@app.get("/users/most-active")
async def get_most_active_users(limit: int = Query(10, ge=1, le=100)):
    """Get users with most ratings"""
    if ratings_df is None or ratings_df.empty:
        return []
    
    user_stats = ratings_df.groupby('User-ID').agg({
        'Book-Rating': ['count', 'mean']
    }).reset_index()
    
    user_stats.columns = ['User-ID', 'total_ratings', 'average_rating']
    user_stats = user_stats.sort_values('total_ratings', ascending=False).head(limit)
    
    return user_stats.to_dict('records')

# Search ratings by rating value
@app.get("/ratings/by-value/{rating_value}")
async def get_ratings_by_value(
    rating_value: int = Field(..., ge=0, le=10),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all ratings with a specific value"""
    if ratings_df is None or ratings_df.empty:
        return []
    
    filtered_ratings = ratings_df[ratings_df['Book-Rating'] == rating_value]
    
    start = skip
    end = skip + limit
    return filtered_ratings.iloc[start:end].to_dict('records')

# Get overall statistics
@app.get("/stats/overview")
async def get_overview_stats():
    """Get overall statistics of the ratings dataset"""
    if ratings_df is None or ratings_df.empty:
        raise HTTPException(status_code=404, detail="No ratings data available")
    
    return {
        "total_ratings": len(ratings_df),
        "unique_users": int(ratings_df['User-ID'].nunique()),
        "unique_books": int(ratings_df['ISBN'].nunique()),
        "average_rating": float(ratings_df['Book-Rating'].mean()),
        "median_rating": float(ratings_df['Book-Rating'].median()),
        "rating_distribution": ratings_df['Book-Rating'].value_counts().to_dict()
    }

# Create new rating
@app.post("/ratings", status_code=201)
async def create_rating(rating: RatingCreate):
    """Create a new rating (in-memory only, not persisted to CSV)"""
    global ratings_df
    
    if ratings_df is None:
        raise HTTPException(status_code=500, detail="Ratings data not loaded")
    
    # Check if rating already exists
    existing = ratings_df[
        (ratings_df['User-ID'] == rating.user_id) & 
        (ratings_df['ISBN'] == rating.isbn)
    ]
    
    if not existing.empty:
        raise HTTPException(status_code=400, detail="Rating already exists for this user and book")
    
    # Add new rating to dataframe (in-memory only)
    new_row = pd.DataFrame([{
        'User-ID': rating.user_id,
        'ISBN': rating.isbn,
        'Book-Rating': rating.rating
    }])
    
    ratings_df = pd.concat([ratings_df, new_row], ignore_index=True)
    
    return {
        "message": "Rating created successfully",
        "rating": {
            "user_id": rating.user_id,
            "isbn": rating.isbn,
            "rating": rating.rating
        }
    }

# Update rating
@app.put("/ratings/{user_id}/{isbn}")
async def update_rating(user_id: int, isbn: str, new_rating: int = Field(..., ge=0, le=10)):
    """Update an existing rating (in-memory only)"""
    global ratings_df
    
    if ratings_df is None:
        raise HTTPException(status_code=500, detail="Ratings data not loaded")
    
    # Find the rating
    mask = (ratings_df['User-ID'] == user_id) & (ratings_df['ISBN'] == isbn)
    
    if not ratings_df[mask].any().any():
        raise HTTPException(status_code=404, detail="Rating not found")
    
    # Update the rating
    ratings_df.loc[mask, 'Book-Rating'] = new_rating
    
    return {
        "message": "Rating updated successfully",
        "user_id": user_id,
        "isbn": isbn,
        "new_rating": new_rating
    }

# Delete rating
@app.delete("/ratings/{user_id}/{isbn}")
async def delete_rating(user_id: int, isbn: str):
    """Delete a rating (in-memory only)"""
    global ratings_df
    
    if ratings_df is None:
        raise HTTPException(status_code=500, detail="Ratings data not loaded")
    
    # Find the rating
    mask = (ratings_df['User-ID'] == user_id) & (ratings_df['ISBN'] == isbn)
    
    if not ratings_df[mask].any().any():
        raise HTTPException(status_code=404, detail="Rating not found")
    
    # Delete the rating
    ratings_df = ratings_df[~mask]
    
    return {"message": "Rating deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)