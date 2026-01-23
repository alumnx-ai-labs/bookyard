# app/schemas/dataset_schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class LoadSourceEnum(str, Enum):
    """Enum for dataset load source"""
    LOCAL = "local"
    UPLOAD = "upload"

class DatasetLoadRequest(BaseModel):
    """Request schema for loading datasets"""
    source: LoadSourceEnum = Field(
        default=LoadSourceEnum.LOCAL,
        description="Source of datasets: 'local' (from /data folder) or 'upload' (file upload)"
    )
    nrows: Optional[int] = Field(
        default=15000,
        description="Number of rows to load (for testing/optimization)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "source": "local",
                "nrows": 15000
            }
        }

class DatasetStatistics(BaseModel):
    """Statistics about loaded datasets"""
    total_users: int = Field(..., description="Total number of users")
    total_books: int = Field(..., description="Total number of books")
    total_ratings: int = Field(..., description="Total number of ratings")
    avg_ratings_per_user: float = Field(..., description="Average ratings per user")
    sparsity: float = Field(..., description="Matrix sparsity (0-1)")

class DatasetLoadResponse(BaseModel):
    """Response schema for dataset loading"""
    status: str = Field(..., description="Status: 'success' or 'error'")
    message: str = Field(..., description="Status message")
    statistics: Optional[DatasetStatistics] = Field(
        default=None,
        description="Dataset statistics if successful"
    )

class DatasetStatusResponse(BaseModel):
    """Response schema for dataset status"""
    status: str = Field(..., description="'loaded' or 'not_loaded'")
    message: str = Field(..., description="Status message")
    users: Optional[int] = Field(default=None)
    books: Optional[int] = Field(default=None)
    total_ratings: Optional[int] = Field(default=None)

class RecommendationRequest(BaseModel):
    """Request schema for getting recommendations"""
    user_id: int = Field(..., description="User ID to get recommendations for", gt=0)
    k: int = Field(
        default=10,
        description="Number of similar users to consider",
        ge=1,
        le=100
    )
    top_n: int = Field(
        default=10,
        description="Number of books to recommend",
        ge=1,
        le=50
    )
    
    @validator('user_id')
    def user_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('User ID must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 123,
                "k": 10,
                "top_n": 10
            }
        }

class RecommendedBook(BaseModel):
    """Schema for a recommended book"""
    ISBN: str = Field(..., description="Book ISBN")
    BookTitle: str = Field(..., alias="Book-Title", description="Title of the book")
    BookAuthor: str = Field(..., alias="Book-Author", description="Author of the book")
    YearOfPublication: int = Field(..., alias="Year-Of-Publication", description="Publication year")
    Publisher: str = Field(..., description="Publisher name")
    PredictedRating: float = Field(..., alias="Predicted-Rating", description="Predicted rating (0-10)")
    
    class Config:
        populate_by_name = True

class RecommendationResponse(BaseModel):
    """Response schema for recommendations"""
    status: str = Field(..., description="'success' or 'error'")
    user_id: int = Field(..., description="User ID")
    message: Optional[str] = Field(default=None, description="Message (if error)")
    total_recommendations: Optional[int] = Field(default=None)
    recommendations: Optional[List[Dict[str, Any]]] = Field(default=None)
    parameters: Optional[Dict[str, int]] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "user_id": 123,
                "total_recommendations": 10,
                "recommendations": [
                    {
                        "ISBN": "0451524934",
                        "Book-Title": "The Great Gatsby",
                        "Book-Author": "F. Scott Fitzgerald",
                        "Year-Of-Publication": 2004,
                        "Publisher": "Penguin Classics",
                        "Predicted-Rating": 8.5
                    }
                ],
                "parameters": {
                    "k_similar_users": 10,
                    "top_n_books": 10
                }
            }
        }