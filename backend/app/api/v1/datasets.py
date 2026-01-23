# app/api/v1/datasets.py
from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import logging
from typing import Optional
import numpy as np

from app.schemas.dataset_schemas import (
    DatasetLoadRequest,
    DatasetLoadResponse,
    DatasetStatusResponse,
    RecommendationRequest,
    RecommendationResponse
)
from app.services.dataset_service import DatasetService
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter(
    prefix="/api/v1/datasets",
    tags=["datasets"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)

# Configuration
DATA_FOLDER = Path(__file__).parent.parent.parent.parent / "data"

@router.post(
    "/load",
    response_model=DatasetLoadResponse,
    summary="Load datasets",
    description="Load Books, Ratings, and Users datasets from local folder or uploaded files"
)
async def load_datasets(request: DatasetLoadRequest):
    """
    Load datasets for the recommendation system from /data folder.
    
    **Parameters:**
    - source: "local" (loads from /data folder)
    - nrows: Optional number of rows to load (default: 15000)
    
    **Expected files in /data folder:**
    - Books.csv
    - Book-Ratings.csv
    - Users.csv
    """
    
    try:
        dataset_service = DatasetService()
        
        # Load from /data folder
        books_path = DATA_FOLDER / "Books.csv"
        ratings_path = DATA_FOLDER / "Book-Ratings.csv"
        users_path = DATA_FOLDER / "Users.csv"
        
        # Verify files exist
        missing_files = []
        for name, file_path in [
            ("Books.csv", books_path),
            ("Book-Ratings.csv", ratings_path),
            ("Users.csv", users_path)
        ]:
            if not file_path.exists():
                missing_files.append(f"{name} (expected at: {file_path})")
        
        if missing_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Missing files in /data folder: {', '.join(missing_files)}"
            )
        
        logger.info(f"Loading datasets from {DATA_FOLDER}")
        result = dataset_service.load_datasets(
            books_path=str(books_path),
            ratings_path=str(ratings_path),
            users_path=str(users_path),
            nrows=request.nrows
        )
        
        return DatasetLoadResponse(
            status=result["status"],
            message=result["message"],
            statistics=result.get("statistics")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading datasets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading datasets: {str(e)}"
        )

@router.get(
    "/status",
    response_model=DatasetStatusResponse,
    summary="Check dataset status",
    description="Check if datasets are loaded and get basic statistics"
)
async def get_dataset_status():
    """
    Get current status of loaded datasets.
    
    **Returns:**
    - status: "loaded" or "not_loaded"
    - statistics: Users, books, and total ratings count
    """
    try:
        dataset_service = DatasetService()
        status_info = dataset_service.get_status()
        return DatasetStatusResponse(**status_info)
    
    except Exception as e:
        logger.error(f"Error getting dataset status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dataset status: {str(e)}"
        )

@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Get book recommendations",
    description="Generate personalized book recommendations for a specific user"
)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized book recommendations for a user.
    
    Uses collaborative filtering based on similar users' ratings.
    
    **Parameters:**
    - user_id: User ID to get recommendations for (required)
    - k: Number of similar users to consider (default: 10)
    - top_n: Number of books to recommend (default: 10)
    
    **Returns:**
    - List of recommended books with details and predicted ratings
    """
    
    try:
        dataset_service = DatasetService()
        
        if not dataset_service.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datasets not loaded. Please load datasets first using /load endpoint"
            )
        
        recommendations = RecommendationEngine.get_recommendations_dict(
            user_id=request.user_id,
            k=request.k,
            top_n=request.top_n
        )
        
        if recommendations["status"] == "error":
            return RecommendationResponse(
                status="error",
                user_id=request.user_id,
                message=recommendations["message"]
            )
        
        return RecommendationResponse(**recommendations)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get(
    "/users",
    summary="Get available users",
    description="Get list of available user IDs for recommendations"
)
async def get_available_users(limit: int = 20):
    """
    Get available user IDs from loaded datasets.
    
    **Parameters:**
    - limit: Number of user IDs to return (default: 20)
    
    **Returns:**
    - List of user IDs that can be used for recommendations
    """
    try:
        dataset_service = DatasetService()
        
        if not dataset_service.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datasets not loaded. Please load datasets first using /load endpoint"
            )
        
        user_ids = list(dataset_service._user_book_matrix.index[:limit])
        
        return {
            "status": "success",
            "total_available_users": len(dataset_service._user_book_matrix),
            "sample_user_ids": user_ids,
            "limit_requested": limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user IDs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user IDs: {str(e)}"
        )
    


@router.post(
    "/validate-recommendations",
    summary="Validate recommendations for a user",
    description="Provides detailed validation checks including user history and recommendation quality"
)
async def validate_recommendations(
    user_id: int,
    top_n: int = 10
):
    """
    Validate recommendations with detailed checks:
    1. User's rating history (already rated books)
    2. Recommended books (new suggestions)
    3. Validation checks (no duplicates, all unrated, etc.)
    
    **Parameters:**
    - user_id: User ID to validate for
    - top_n: Number of recommendations to validate (default: 10)
    
    **Returns:**
    - User's rated books
    - Recommended books with details
    - Validation checks results
    """
    
    try:
        dataset_service = DatasetService()
        
        if not dataset_service.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datasets not loaded. Please load datasets first using /load endpoint"
            )
        
        try:
            # Get user index to verify user exists
            user_book_matrix = dataset_service._user_book_matrix
            user_index = user_book_matrix.index.get_loc(user_id)
            
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID {user_id} not found in the dataset"
            )
        
        # Get user's rated books
        ratings_matrix = user_book_matrix.to_numpy()
        user_rated_mask = ratings_matrix[user_index] > 0
        user_rated_isbns = user_book_matrix.columns[user_rated_mask].tolist()
        
        # Get user's rated books details
        books_data = dataset_service._books_data
        user_history_df = books_data[books_data["ISBN"].isin(user_rated_isbns)][
            ["ISBN", "Book-Title", "Book-Author", "Year-Of-Publication", "Publisher"]
        ].copy()
        
        # Get user's actual ratings
        user_ratings_dict = {}
        for isbn in user_rated_isbns:
            col_idx = user_book_matrix.columns.get_loc(isbn)
            user_ratings_dict[isbn] = int(ratings_matrix[user_index][col_idx])
        
        user_history_df["User-Rating"] = user_history_df["ISBN"].map(user_ratings_dict)
        user_history_list = user_history_df.to_dict('records')
        
        # Get recommendations
        recommendations_df = RecommendationEngine.recommend_books(
            user_id=user_id,
            k=10,
            top_n=top_n
        )
        
        if isinstance(recommendations_df, str):
            return {
                "status": "error",
                "user_id": user_id,
                "message": recommendations_df,
                "user_history": {
                    "total_rated": len(user_rated_isbns),
                    "books": user_history_list
                }
            }
        
        recommendations_list = recommendations_df.to_dict('records')
        recommended_isbns = recommendations_df["ISBN"].tolist()
        
        # Validation checks
        validation_checks = {
            "no_duplicates": len(set(recommended_isbns)) == len(recommended_isbns),
            "all_unrated": all(
                isbn not in user_rated_isbns 
                for isbn in recommended_isbns
            ),
            "recommendations_count": len(recommendations_list),
            "avg_predicted_rating": round(
                recommendations_df["Predicted-Rating"].mean(), 2
            ),
            "min_predicted_rating": round(
                recommendations_df["Predicted-Rating"].min(), 2
            ),
            "max_predicted_rating": round(
                recommendations_df["Predicted-Rating"].max(), 2
            ),
            "unique_authors": len(recommendations_df["Book-Author"].unique()),
            "author_diversity_percentage": round(
                (len(recommendations_df["Book-Author"].unique()) / len(recommendations_list)) * 100, 2
            )
        }
        
        # Quality assessment
        quality_score = 0
        quality_reasons = []
        
        if validation_checks["no_duplicates"]:
            quality_score += 20
            quality_reasons.append("✅ No duplicates")
        else:
            quality_reasons.append("❌ Found duplicates")
        
        if validation_checks["all_unrated"]:
            quality_score += 20
            quality_reasons.append("✅ All books unrated by user")
        else:
            quality_reasons.append("❌ Some books already rated by user")
        
        if validation_checks["avg_predicted_rating"] >= 7.5:
            quality_score += 20
            quality_reasons.append(f"✅ High confidence (avg rating: {validation_checks['avg_predicted_rating']})")
        elif validation_checks["avg_predicted_rating"] >= 6.5:
            quality_score += 10
            quality_reasons.append(f"⚠️ Moderate confidence (avg rating: {validation_checks['avg_predicted_rating']})")
        else:
            quality_reasons.append(f"❌ Low confidence (avg rating: {validation_checks['avg_predicted_rating']})")
        
        if validation_checks["author_diversity_percentage"] >= 70:
            quality_score += 20
            quality_reasons.append(f"✅ Good author diversity ({validation_checks['author_diversity_percentage']}%)")
        elif validation_checks["author_diversity_percentage"] >= 50:
            quality_score += 10
            quality_reasons.append(f"⚠️ Moderate diversity ({validation_checks['author_diversity_percentage']}%)")
        else:
            quality_reasons.append(f"❌ Low diversity ({validation_checks['author_diversity_percentage']}%)")
        
        quality_score += 20  # Base score
        
        return {
            "status": "success",
            "user_id": user_id,
            "user_history": {
                "total_rated": len(user_rated_isbns),
                "books": user_history_list
            },
            "recommendations": {
                "total": len(recommendations_list),
                "books": recommendations_list
            },
            "validation_checks": validation_checks,
            "quality_assessment": {
                "overall_score": min(quality_score, 100),
                "rating": (
                    "Excellent" if quality_score >= 80 else
                    "Good" if quality_score >= 60 else
                    "Fair" if quality_score >= 40 else
                    "Poor"
                ),
                "reasons": quality_reasons
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating recommendations: {str(e)}"
        )

@router.post(
    "/explain-recommendations",
    summary="Explain why books are recommended",
    description="Shows detailed explanation for each recommendation including similar users and their ratings"
)
async def explain_recommendations(
    user_id: int,
    top_n: int = 5,
    show_similar_users: int = 5
):
    """
    Explain recommendations by showing:
    1. Which similar users rated the book highly
    2. Their rating and similarity score
    3. Why this book was recommended
    
    **Parameters:**
    - user_id: User ID to explain recommendations for
    - top_n: Number of recommendations to explain (default: 5)
    - show_similar_users: Number of similar users to show (default: 5)
    
    **Returns:**
    - Detailed explanation for each book
    - List of similar users who rated it highly
    - Recommendation confidence
    """
    
    try:
        dataset_service = DatasetService()
        
        if not dataset_service.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datasets not loaded. Please load datasets first using /load endpoint"
            )
        
        try:
            # Get user index to verify user exists
            user_book_matrix = dataset_service._user_book_matrix
            user_index = user_book_matrix.index.get_loc(user_id)
            
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID {user_id} not found in the dataset"
            )
        
        # Get recommendations
        recommendations_df = RecommendationEngine.recommend_books(
            user_id=user_id,
            k=10,
            top_n=top_n
        )
        
        if isinstance(recommendations_df, str):
            return {
                "status": "error",
                "user_id": user_id,
                "message": recommendations_df
            }
        
        # Get data for explanations
        user_similarity = dataset_service._user_similarity
        ratings_data = dataset_service._ratings_data
        
        ratings_matrix = user_book_matrix.to_numpy()
        
        # Find k most similar users
        similarity_scores = user_similarity[user_index].copy()
        similarity_scores[similarity_scores <= 0] = 0
        similar_users_indices = np.argsort(similarity_scores)[::-1][1:11]
        similar_users_indices = similar_users_indices[
            similarity_scores[similar_users_indices] > 0
        ]
        
        explanations = []
        
        for idx, row in recommendations_df.iterrows():
            isbn = row["ISBN"]
            predicted_rating = row["Predicted-Rating"]
            
            # Find users who rated this book highly (≥4)
            high_raters = ratings_data[
                (ratings_data["ISBN"] == isbn) & 
                (ratings_data["Book-Rating"] >= 4)
            ].copy()
            
            # Get details of similar users who rated it
            similar_high_raters = []
            
            for sim_user_idx in similar_users_indices:
                sim_user_id = user_book_matrix.index[sim_user_idx]
                
                # Get this user's rating for the book
                col_idx = user_book_matrix.columns.get_loc(isbn)
                rating = ratings_matrix[sim_user_idx][col_idx]
                
                if rating >= 4:  # They rated it highly
                    similarity_score = float(similarity_scores[sim_user_idx])
                    
                    similar_high_raters.append({
                        "user_id": int(sim_user_id),
                        "rating": int(rating),
                        "similarity_score": round(similarity_score, 4),
                        "similarity_percentage": round(similarity_score * 100, 2)
                    })
            
            # Sort by similarity
            similar_high_raters.sort(
                key=lambda x: x["similarity_score"],
                reverse=True
            )
            similar_high_raters = similar_high_raters[:show_similar_users]
            
            explanation = {
                "isbn": isbn,
                "book_title": row["Book-Title"],
                "book_author": row["Book-Author"],
                "year": int(row["Year-Of-Publication"]),
                "publisher": row["Publisher"],
                "predicted_rating": round(predicted_rating, 2),
                "confidence_level": (
                    "Very High" if predicted_rating >= 8.5 else
                    "High" if predicted_rating >= 7.5 else
                    "Medium" if predicted_rating >= 6.5 else
                    "Low"
                ),
                "why_recommended": "Similar users rated this book highly",
                "total_high_raters": int(len(high_raters)),
                "similar_users_who_rated_highly": similar_high_raters,
                "recommendation_reason": (
                    f"Based on {len(similar_high_raters)} similar user(s) who rated this book "
                    f"{'highly' if len(similar_high_raters) > 0 else 'moderately'}"
                )
            }
            
            explanations.append(explanation)
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_recommendations": len(explanations),
            "explanations": explanations,
            "summary": {
                "average_predicted_rating": round(
                    recommendations_df["Predicted-Rating"].mean(), 2
                ),
                "total_unique_similar_users_involved": len(similar_users_indices),
                "explanation_method": "Collaborative Filtering - Based on Similar Users' Preferences"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error explaining recommendations: {str(e)}"
        )

@router.post(
    "/diagnose-user",
    summary="Diagnose why recommendations are poor for a user",
    description="Detailed analysis of why recommendations might be low quality"
)
async def diagnose_user(user_id: int):
    """
    Diagnose issues with recommendations for a user.
    
    Shows:
    1. User's rating history
    2. Similar users analysis
    3. Data sparsity issues
    4. Recommendations for improvement
    
    **Parameters:**
    - user_id: User ID to diagnose
    
    **Returns:**
    - Detailed diagnosis report
    """
    
    try:
        dataset_service = DatasetService()
        
        if not dataset_service.is_loaded():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datasets not loaded"
            )
        
        try:
            user_book_matrix = dataset_service._user_book_matrix
            user_index = user_book_matrix.index.get_loc(user_id)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID {user_id} not found"
            )
        
        ratings_matrix = user_book_matrix.to_numpy()
        user_similarity = dataset_service._user_similarity
        
        # 1. User's Rating History
        user_rated_mask = ratings_matrix[user_index] > 0
        user_rated_count = int(np.sum(user_rated_mask))
        user_rated_books = user_book_matrix.columns[user_rated_mask].tolist()
        
        # Get user's actual ratings
        user_ratings_list = []
        books_data = dataset_service._books_data
        for isbn in user_rated_books[:10]:  # Show first 10 books
            col_idx = user_book_matrix.columns.get_loc(isbn)
            rating = int(ratings_matrix[user_index][col_idx])
            
            book_info = books_data[books_data["ISBN"] == isbn][
                ["ISBN", "Book-Title", "Book-Author"]
            ].to_dict('records')
            
            if book_info:
                user_ratings_list.append({
                    "ISBN": str(book_info[0]["ISBN"]),
                    "Book-Title": str(book_info[0]["Book-Title"]),
                    "Book-Author": str(book_info[0]["Book-Author"]),
                    "User-Rating": rating
                })
        
        # 2. Similar Users Analysis
        similarity_scores = user_similarity[user_index].copy()
        similarity_scores[similarity_scores <= 0] = 0
        
        # Get top similar users
        top_similar_indices = np.argsort(similarity_scores)[::-1][1:21]
        top_similar_indices = top_similar_indices[similarity_scores[top_similar_indices] > 0]
        
        similar_users_analysis = []
        for sim_idx in top_similar_indices:
            sim_user_id = user_book_matrix.index[sim_idx]
            sim_score = float(similarity_scores[sim_idx])
            
            # Count overlapping ratings
            sim_rated_mask = ratings_matrix[sim_idx] > 0
            overlap = int(np.sum(user_rated_mask & sim_rated_mask))
            
            similar_users_analysis.append({
                "user_id": int(sim_user_id),
                "similarity_score": round(sim_score, 4),
                "similarity_percentage": round(sim_score * 100, 2),
                "overlapping_rated_books": overlap,
                "their_total_ratings": int(np.sum(sim_rated_mask))
            })
        
        # 3. Data Sparsity Analysis
        total_users = int(ratings_matrix.shape[0])
        total_books = int(ratings_matrix.shape[1])
        total_possible = total_users * total_books
        total_ratings = int(np.count_nonzero(ratings_matrix))
        sparsity = float(1 - (total_ratings / total_possible))
        
        # User-specific sparsity
        user_rated_percentage = float((user_rated_count / total_books) * 100)
        
        # 4. Calculate average similarity and statistics
        if similar_users_analysis:
            avg_similarity_percentage = float(np.mean([u["similarity_percentage"] for u in similar_users_analysis]))
            max_similarity_percentage = float(similar_users_analysis[0]["similarity_percentage"])
        else:
            avg_similarity_percentage = 0.0
            max_similarity_percentage = 0.0
        
        # 5. Diagnosis and Recommendations
        issues = []
        recommendations = []
        
        if len(top_similar_indices) < 3:
            issues.append(f"❌ Only {len(top_similar_indices)} similar users found (need ≥3)")
            recommendations.append("Load more data (increase nrows in /load endpoint)")
        
        if len(top_similar_indices) >= 1 and max_similarity_percentage < 30:
            issues.append(f"❌ Very low max similarity ({max_similarity_percentage:.1f}%) - users have very different tastes")
            recommendations.append("User might have unique preferences - consider increasing k parameter or load more data")
        
        if user_rated_count < 5:
            issues.append(f"❌ User has only {user_rated_count} ratings (need ≥5 for good results)")
            recommendations.append("Collect more ratings from this user")
        
        if user_rated_percentage < 1:
            issues.append(f"❌ User rated only {user_rated_percentage:.2f}% of available books")
            recommendations.append("Very sparse data - recommendations will have low confidence")
        
        if sparsity > 0.99:
            issues.append(f"❌ Dataset is extremely sparse ({sparsity*100:.1f}%)")
            recommendations.append("Dataset has too few ratings overall - load all data using nrows=null")
        
        # Calculate quality score
        quality_score = 100
        
        if len(top_similar_indices) < 3:
            quality_score -= 40
        elif len(top_similar_indices) < 5:
            quality_score -= 20
        
        if max_similarity_percentage < 30:
            quality_score -= 30
        elif max_similarity_percentage < 50:
            quality_score -= 15
        
        if user_rated_count < 5:
            quality_score -= 20
        elif user_rated_count < 10:
            quality_score -= 10
        
        if sparsity > 0.99:
            quality_score -= 10
        
        quality_score = max(int(quality_score), 0)
        
        return {
            "status": "success",
            "user_id": user_id,
            "diagnosis": {
                "user_stats": {
                    "total_ratings": user_rated_count,
                    "total_books_in_system": total_books,
                    "rated_percentage": round(user_rated_percentage, 2),
                    "sample_rated_books": user_ratings_list,
                    "activity_level": (
                        "Very Active" if user_rated_count >= 20 else
                        "Active" if user_rated_count >= 10 else
                        "Moderate" if user_rated_count >= 5 else
                        "Low Activity"
                    )
                },
                "similar_users": {
                    "count": len(top_similar_indices),
                    "top_5_similar_users": similar_users_analysis[:5],
                    "all_similar_users": similar_users_analysis,
                    "max_similarity_percentage": round(max_similarity_percentage, 2),
                    "avg_similarity_percentage": round(avg_similarity_percentage, 2),
                    "analysis": (
                        "✅ Good - Have multiple highly similar users" if len(top_similar_indices) >= 5 and max_similarity_percentage >= 50 else
                        "⚠️ Fair - Have some similar users" if len(top_similar_indices) >= 3 and max_similarity_percentage >= 30 else
                        "❌ Poor - Almost no similar users"
                    )
                },
                "data_sparsity": {
                    "total_users": total_users,
                    "total_books": total_books,
                    "total_ratings": total_ratings,
                    "dataset_sparsity": round(sparsity * 100, 2),
                    "analysis": (
                        "✅ Good density" if sparsity < 0.95 else
                        "⚠️ Sparse data" if sparsity < 0.99 else
                        "❌ Very sparse data"
                    )
                }
            },
            "issues": issues if issues else ["✅ No major issues detected"],
            "recommendations": recommendations if recommendations else ["✅ Data looks good for recommendations"],
            "quality_score": quality_score,
            "recommendation_reliability": (
                "High ✅" if quality_score >= 70 else
                "Medium ⚠️" if quality_score >= 40 else
                "Low ❌"
            ),
            "suggested_actions": [
                {
                    "action": "Try with increased k parameter",
                    "command": f"POST /recommendations with user_id={user_id}, k=50, top_n=5",
                    "expected": "Get recommendations from more (less similar) users"
                },
                {
                    "action": "Load more data",
                    "command": "POST /load with nrows=null",
                    "expected": "Better similarity matching, more recommendations"
                },
                {
                    "action": "Check this user's recommendations",
                    "command": f"POST /recommendations with user_id={user_id}",
                    "expected": "See if recommendations are available"
                }
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error diagnosing user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# Health check endpoint
@router.get(
    "/health",
    summary="Health check",
    description="Check if the datasets service is running"
)
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "ok",
        "service": "datasets-recommendation"
    }