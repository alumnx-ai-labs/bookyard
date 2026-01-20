# app/services/recommendation_engine.py
import pandas as pd
import numpy as np
import logging
from typing import Union, List
from .dataset_service import DatasetService

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Service for generating book recommendations using collaborative filtering"""
    
    @staticmethod
    def recommend_books(
        user_id: int,
        k: int = 10,
        top_n: int = 10
    ) -> Union[pd.DataFrame, str]:
        """
        Generate book recommendations for a user using collaborative filtering
        
        Parameters:
        -----------
        user_id : int
            The User-ID to get recommendations for
        k : int
            Number of similar users to consider (default: 10)
        top_n : int
            Number of top books to recommend (default: 10)
            
        Returns:
        --------
        pd.DataFrame or str
            DataFrame with recommendations or error message
        """
        
        dataset = DatasetService()
        
        if not dataset._is_loaded:
            return "Datasets not loaded. Please load datasets first."
        
        try:
            # Get user index
            user_book_matrix = dataset._user_book_matrix
            user_similarity = dataset._user_similarity
            books_data = dataset._books_data
            
            user_index = user_book_matrix.index.get_loc(user_id)
            
        except KeyError:
            return f"User ID {user_id} not found in the dataset"
        
        try:
            # Prepare matrices
            ratings_matrix = user_book_matrix.to_numpy()
            
            # Adjust k if necessary
            k = min(k, len(user_book_matrix) - 1)
            
            # Get similarity scores
            similarity_scores = user_similarity[user_index].copy()
            similarity_scores[similarity_scores <= 0] = 0
            
            # Find k most similar users (excluding self)
            similar_users_indices = np.argsort(similarity_scores)[::-1][1:k+1]
            similar_users_indices = similar_users_indices[
                similarity_scores[similar_users_indices] > 0
            ]
            
            if len(similar_users_indices) == 0:
                return "No similar users found for recommendations"
            
            # Calculate weighted average ratings from similar users
            weights = similarity_scores[similar_users_indices]
            weights = weights / np.sum(weights)
            
            avg_book_ratings = np.zeros(ratings_matrix.shape[1])
            for idx, user_idx in enumerate(similar_users_indices):
                user_ratings = ratings_matrix[user_idx]
                avg_book_ratings += user_ratings * weights[idx]
            
            # Exclude already rated books
            user_rated_mask = ratings_matrix[user_index] > 0
            avg_book_ratings[user_rated_mask] = -1
            
            # Get top books
            top_book_indices = np.argsort(avg_book_ratings)[::-1]
            top_book_indices = top_book_indices[
                avg_book_ratings[top_book_indices] >= 0
            ][:top_n]
            
            if len(top_book_indices) == 0:
                return "No new books to recommend"
            
            # Get book details
            recommended_isbns = user_book_matrix.columns[top_book_indices]
            
            recommended_books = books_data[books_data["ISBN"].isin(recommended_isbns)][
                ["ISBN", "Book-Title", "Book-Author", "Year-Of-Publication", "Publisher"]
            ].copy()
            
            # Add predicted ratings
            predicted_ratings = []
            for isbn in recommended_books["ISBN"]:
                col_idx = user_book_matrix.columns.get_loc(isbn)
                predicted_ratings.append(avg_book_ratings[col_idx])
            
            recommended_books["Predicted-Rating"] = predicted_ratings
            recommended_books = recommended_books.sort_values(
                "Predicted-Rating",
                ascending=False
            )
            
            # FILTER: Only keep books with predicted rating >= 5.0
            recommended_books = recommended_books[
                recommended_books["Predicted-Rating"] >= 5.0
            ]
            
            # If no high-confidence books, return what we have with warning
            if len(recommended_books) == 0:
                logger.warning(f"User {user_id}: No high-confidence recommendations (all < 5.0)")
                return "Not enough high-confidence recommendations available"
            
            # Limit to top_n after filtering
            recommended_books = recommended_books.head(top_n)
            
            logger.info(f"Generated {len(recommended_books)} recommendations for user {user_id}")
            return recommended_books
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"Error generating recommendations: {str(e)}"
    
    @staticmethod
    def get_recommendations_dict(
        user_id: int,
        k: int = 10,
        top_n: int = 10
    ) -> dict:
        """
        Get recommendations as a dictionary (for API responses)
        
        Returns:
        --------
        dict : Contains status, recommendations list, and metadata
        """
        
        recommendations_df = RecommendationEngine.recommend_books(user_id, k, top_n)
        
        if isinstance(recommendations_df, str):
            return {
                "status": "error",
                "message": recommendations_df,
                "user_id": user_id
            }
        
        recommendations_list = recommendations_df.to_dict('records')
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_recommendations": len(recommendations_list),
            "recommendations": recommendations_list,
            "parameters": {
                "k_similar_users": k,
                "top_n_books": top_n
            }
        }