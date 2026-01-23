import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings

warnings.filterwarnings('ignore')

# Global variables - will be populated when datasets are loaded
books_data = None
ratings_data = None
users_data = None
user_book_matrix = None
user_similarity = None

def load_datasets_into_memory(books_path, ratings_path, users_path, nrows=15000):
    """Load datasets into global variables"""
    global books_data, ratings_data, users_data, user_book_matrix, user_similarity
    
    print(f"Loading datasets...")
    
    books_data = pd.read_csv(
        books_path,
        nrows=nrows,
        encoding='latin1',
        sep=';',
        on_bad_lines='skip'
    )
    
    ratings_data = pd.read_csv(
        ratings_path,
        nrows=nrows,
        encoding='latin1',
        sep=';',
        on_bad_lines='skip'
    )
    
    users_data = pd.read_csv(
        users_path,
        nrows=nrows,
        encoding='latin1',
        sep=';',
        on_bad_lines='skip'
    )
    
    print("Datasets loaded. Processing...")
    
    # Remove ratings with 0 values
    ratings_data = ratings_data[ratings_data["Book-Rating"] > 0]
    
    # Merge datasets
    merged_df = pd.merge(ratings_data, books_data, on="ISBN")
    merged_df = pd.merge(merged_df, users_data, on="User-ID")
    
    # Filter data
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
    
    # Create user-book matrix
    user_book_matrix = merged_df.pivot_table(
        index="User-ID",
        columns="ISBN",
        values="Book-Rating",
        fill_value=0
    )
    
    print(f"User-Book Matrix Shape: {user_book_matrix.shape}")
    
    # Compute user similarity
    print("Computing user similarity matrix...")
    ratings_matrix = user_book_matrix.to_numpy()
    
    # Normalize ratings
    ratings_matrix_normalized = ratings_matrix.copy()
    for i in range(ratings_matrix.shape[0]):
        user_ratings = ratings_matrix[i][ratings_matrix[i] > 0]
        if len(user_ratings) > 0:
            user_mean = np.mean(user_ratings)
            mask = ratings_matrix[i] > 0
            ratings_matrix_normalized[i][mask] -= user_mean
    
    user_similarity = cosine_similarity(ratings_matrix_normalized)
    
    print(f"User Similarity Matrix Shape: {user_similarity.shape}")
    print("Datasets ready for recommendations!")

def recommend_books(user_id, k=10, top_n=10):
    """
    Recommend books for a user using collaborative filtering
    
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
    
    global books_data, user_book_matrix, user_similarity
    
    if user_book_matrix is None:
        return "Datasets not loaded. Please load datasets first."
    
    try:
        user_index = user_book_matrix.index.get_loc(user_id)
    except KeyError:
        return f"User ID {user_id} not found in the dataset"
    
    try:
        ratings_matrix = user_book_matrix.to_numpy()
        
        # Adjust k if necessary
        k = min(k, len(user_book_matrix) - 1)
        
        # Get similarity scores
        similarity_scores = user_similarity[user_index].copy()
        similarity_scores[similarity_scores <= 0] = 0
        
        # Find k most similar users
        similar_users_indices = np.argsort(similarity_scores)[::-1][1:k+1]
        similar_users_indices = similar_users_indices[
            similarity_scores[similar_users_indices] > 0
        ]
        
        if len(similar_users_indices) == 0:
            return "No similar users found for recommendations"
        
        # Calculate weighted average ratings
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
        
        return recommended_books
        
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def book_recommender(user_id, k=10, top_n=10):
    """
    Wrapper function for book recommendations
    
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
    
    recommendations = recommend_books(user_id=user_id, k=k, top_n=top_n)
    
    if isinstance(recommendations, str):
        return recommendations
    
    return recommendations.reset_index(drop=True)