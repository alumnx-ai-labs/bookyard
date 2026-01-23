# app/services/dataset_service.py
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DatasetService:
    """Service for loading and managing datasets"""
    
    _instance = None
    _books_data = None
    _ratings_data = None
    _users_data = None
    _user_book_matrix = None
    _user_similarity = None
    _is_loaded = False
    
    def __new__(cls):
        """Singleton pattern to maintain single instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_datasets(
        cls,
        books_path: str,
        ratings_path: str,
        users_path: str,
        nrows: Optional[int] = 15000
    ) -> dict:
        """
        Load CSV datasets and prepare recommendation matrices
        
        Parameters:
        -----------
        books_path : str
            Path to Books.csv
        ratings_path : str
            Path to Book-Ratings.csv
        users_path : str
            Path to Users.csv
        nrows : int, optional
            Number of rows to load (for testing). Default: 15000
            
        Returns:
        --------
        dict : Status information
        """
        instance = cls()
        
        try:
            logger.info("Loading datasets...")
            
            # Load CSVs
            instance._books_data = pd.read_csv(
                books_path,
                nrows=nrows,
                encoding='latin1',
                sep=';',
                on_bad_lines='skip'
            )
            
            instance._ratings_data = pd.read_csv(
                ratings_path,
                nrows=nrows,
                encoding='latin1',
                sep=';',
                on_bad_lines='skip'
            )
            
            instance._users_data = pd.read_csv(
                users_path,
                nrows=nrows,
                encoding='latin1',
                sep=';',
                on_bad_lines='skip'
            )
            
            logger.info("Datasets loaded. Processing data...")
            
            # Remove ratings with 0 values (implicit feedback)
            instance._ratings_data = instance._ratings_data[
                instance._ratings_data["Book-Rating"] > 0
            ]
            
            # Merge datasets
            merged_df = pd.merge(
                instance._ratings_data,
                instance._books_data,
                on="ISBN"
            )
            
            merged_df = pd.merge(
                merged_df,
                instance._users_data,
                on="User-ID"
            )
            
            # Filter data for better recommendations
            min_user_ratings = 3
            min_book_ratings = 2
            
            ratings_per_user = merged_df.groupby("User-ID")["Book-Rating"].count()
            users_with_enough_ratings = ratings_per_user[
                ratings_per_user >= min_user_ratings
            ].index
            merged_df = merged_df[merged_df["User-ID"].isin(users_with_enough_ratings)]
            
            ratings_per_book = merged_df.groupby("ISBN")["Book-Rating"].count()
            books_with_enough_ratings = ratings_per_book[
                ratings_per_book >= min_book_ratings
            ].index
            merged_df = merged_df[merged_df["ISBN"].isin(books_with_enough_ratings)]
            
            # Create user-book interaction matrix
            instance._user_book_matrix = merged_df.pivot_table(
                index="User-ID",
                columns="ISBN",
                values="Book-Rating",
                fill_value=0
            )
            
            # Compute user similarity matrix
            logger.info("Computing user similarity matrix...")
            instance._compute_similarity_matrix()
            
            instance._is_loaded = True
            
            status = {
                "status": "success",
                "message": "Datasets loaded successfully",
                "statistics": {
                    "total_users": instance._user_book_matrix.shape[0],
                    "total_books": instance._user_book_matrix.shape[1],
                    "total_ratings": len(merged_df),
                    "avg_ratings_per_user": len(merged_df) / instance._user_book_matrix.shape[0],
                    "sparsity": 1 - (len(merged_df) / (
                        instance._user_book_matrix.shape[0] *
                        instance._user_book_matrix.shape[1]
                    ))
                }
            }
            
            logger.info(f"Successfully loaded: {status}")
            return status
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise Exception(f"Dataset file not found: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            instance._is_loaded = False
            raise Exception(f"Error loading datasets: {str(e)}")
    
    @classmethod
    def _compute_similarity_matrix(cls):
        """Compute user similarity matrix using cosine similarity"""
        from sklearn.metrics.pairwise import cosine_similarity
        
        instance = cls()
        ratings_matrix = instance._user_book_matrix.to_numpy()
        
        # Normalize ratings by user mean
        ratings_matrix_normalized = ratings_matrix.copy()
        
        for i in range(ratings_matrix.shape[0]):
            user_ratings = ratings_matrix[i][ratings_matrix[i] > 0]
            if len(user_ratings) > 0:
                user_mean = np.mean(user_ratings)
                mask = ratings_matrix[i] > 0
                ratings_matrix_normalized[i][mask] -= user_mean
        
        instance._user_similarity = cosine_similarity(ratings_matrix_normalized)
    
    @classmethod
    def is_loaded(cls) -> bool:
        """Check if datasets are loaded"""
        return cls()._is_loaded
    
    @classmethod
    def get_status(cls) -> dict:
        """Get current dataset status"""
        instance = cls()
        
        if not instance._is_loaded:
            return {"status": "not_loaded", "message": "Datasets not loaded yet"}
        
        return {
            "status": "loaded",
            "message": "Datasets ready for recommendations",
            "users": instance._user_book_matrix.shape[0],
            "books": instance._user_book_matrix.shape[1],
            "total_ratings": np.count_nonzero(instance._user_book_matrix.to_numpy())
        }