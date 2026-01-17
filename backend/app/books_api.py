from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import pandas as pd
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Books API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to CSV file
CSV_PATH = Path(__file__).parent / "data" / "Books.csv"

# Load data on startup
books_df = None

@app.on_event("startup")
async def load_data():
    global books_df
    try:
        books_df = pd.read_csv(CSV_PATH, sep=';', encoding='latin-1', on_bad_lines='skip')
        # Clean column names - remove quotes and spaces
        books_df.columns = books_df.columns.str.replace('"', '').str.strip()
        print(f"Loaded {len(books_df)} books")
        print(f"Columns: {list(books_df.columns)}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        # Create empty dataframe with expected columns
        books_df = pd.DataFrame(columns=[
            'ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 
            'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L'
        ])

# Pydantic models
class Book(BaseModel):
    isbn: str = Field(..., alias="ISBN")
    title: str = Field(..., alias="Book-Title")
    author: str = Field(..., alias="Book-Author")
    year: Optional[str] = Field(None, alias="Year-Of-Publication")
    publisher: Optional[str] = Field(None, alias="Publisher")
    image_url_s: Optional[str] = Field(None, alias="Image-URL-S")
    image_url_m: Optional[str] = Field(None, alias="Image-URL-M")
    image_url_l: Optional[str] = Field(None, alias="Image-URL-L")

    class Config:
        populate_by_name = True

class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    year: Optional[str] = None
    publisher: Optional[str] = None
    image_url_s: Optional[str] = None
    image_url_m: Optional[str] = None
    image_url_l: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[str] = None
    publisher: Optional[str] = None
    image_url_s: Optional[str] = None
    image_url_m: Optional[str] = None
    image_url_l: Optional[str] = None

class BookStats(BaseModel):
    total_books: int
    unique_authors: int
    unique_publishers: int
    year_range: dict
    top_authors: List[dict]
    top_publishers: List[dict]

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Books API",
        "version": "1.0.0",
        "total_books": len(books_df) if books_df is not None else 0
    }

# Get all books with pagination
@app.get("/books", response_model=List[Book])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all books with pagination"""
    if books_df is None or books_df.empty:
        return []
    
    start = skip
    end = skip + limit
    data = books_df.iloc[start:end].to_dict('records')
    return data

# Get book by ISBN
@app.get("/books/{isbn}", response_model=Book)
async def get_book(isbn: str):
    """Get a specific book by ISBN"""
    if books_df is None or books_df.empty:
        raise HTTPException(status_code=404, detail="No books data available")
    
    book = books_df[books_df['ISBN'] == isbn]
    
    if book.empty:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return book.iloc[0].to_dict()

# Search books by title
@app.get("/books/search/title")
async def search_by_title(
    title: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search books by title (case-insensitive partial match)"""
    if books_df is None or books_df.empty:
        return []
    
    filtered_books = books_df[
        books_df['Book-Title'].str.contains(title, case=False, na=False)
    ]
    
    if filtered_books.empty:
        return []
    
    start = skip
    end = skip + limit
    return filtered_books.iloc[start:end].to_dict('records')

# Search books by author
@app.get("/books/search/author")
async def search_by_author(
    author: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search books by author (case-insensitive partial match)"""
    if books_df is None or books_df.empty:
        return []
    
    filtered_books = books_df[
        books_df['Book-Author'].str.contains(author, case=False, na=False)
    ]
    
    if filtered_books.empty:
        return []
    
    start = skip
    end = skip + limit
    return filtered_books.iloc[start:end].to_dict('records')

# Search books by publisher
@app.get("/books/search/publisher")
async def search_by_publisher(
    publisher: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search books by publisher (case-insensitive partial match)"""
    if books_df is None or books_df.empty:
        return []
    
    filtered_books = books_df[
        books_df['Publisher'].str.contains(publisher, case=False, na=False)
    ]
    
    if filtered_books.empty:
        return []
    
    start = skip
    end = skip + limit
    return filtered_books.iloc[start:end].to_dict('records')

# Get books by year range
@app.get("/books/year-range")
async def get_books_by_year_range(
    start_year: Optional[int] = Query(None, ge=1000, le=2100),
    end_year: Optional[int] = Query(None, ge=1000, le=2100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get books within a specific year range"""
    if books_df is None or books_df.empty:
        return []
    
    # Convert year to numeric, handling errors
    filtered_books = books_df.copy()
    filtered_books['Year-Numeric'] = pd.to_numeric(
        filtered_books['Year-Of-Publication'], 
        errors='coerce'
    )
    
    # Remove null years
    filtered_books = filtered_books[filtered_books['Year-Numeric'].notna()]
    
    if start_year is not None:
        filtered_books = filtered_books[filtered_books['Year-Numeric'] >= start_year]
    
    if end_year is not None:
        filtered_books = filtered_books[filtered_books['Year-Numeric'] <= end_year]
    
    if filtered_books.empty:
        return []
    
    # Drop the temporary column
    filtered_books = filtered_books.drop('Year-Numeric', axis=1)
    
    start_idx = skip
    end_idx = skip + limit
    return filtered_books.iloc[start_idx:end_idx].to_dict('records')

# Get books by specific author
@app.get("/authors/{author}/books")
async def get_books_by_author(
    author: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all books by a specific author (exact match, case-insensitive)"""
    if books_df is None or books_df.empty:
        return []
    
    author_books = books_df[
        books_df['Book-Author'].str.lower() == author.lower()
    ]
    
    if author_books.empty:
        raise HTTPException(status_code=404, detail="Author not found or has no books")
    
    start = skip
    end = skip + limit
    return author_books.iloc[start:end].to_dict('records')

# Get books by specific publisher
@app.get("/publishers/{publisher}/books")
async def get_books_by_publisher(
    publisher: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all books by a specific publisher (exact match, case-insensitive)"""
    if books_df is None or books_df.empty:
        return []
    
    publisher_books = books_df[
        books_df['Publisher'].str.lower() == publisher.lower()
    ]
    
    if publisher_books.empty:
        raise HTTPException(status_code=404, detail="Publisher not found or has no books")
    
    start = skip
    end = skip + limit
    return publisher_books.iloc[start:end].to_dict('records')

# Get overall statistics
@app.get("/books/stats/overview", response_model=BookStats)
async def get_books_stats():
    """Get overall statistics about books"""
    if books_df is None or books_df.empty:
        raise HTTPException(status_code=404, detail="No books data available")
    
    # Author statistics
    author_counts = books_df['Book-Author'].value_counts()
    top_authors = [
        {"author": author, "book_count": int(count)}
        for author, count in author_counts.head(10).items()
    ]
    
    # Publisher statistics
    publisher_counts = books_df['Publisher'].value_counts()
    top_publishers = [
        {"publisher": publisher, "book_count": int(count)}
        for publisher, count in publisher_counts.head(10).items()
    ]
    
    # Year statistics
    year_data = pd.to_numeric(books_df['Year-Of-Publication'], errors='coerce')
    year_data = year_data.dropna()
    
    year_range = {
        "earliest": int(year_data.min()) if len(year_data) > 0 else None,
        "latest": int(year_data.max()) if len(year_data) > 0 else None,
        "median": int(year_data.median()) if len(year_data) > 0 else None
    }
    
    return {
        "total_books": len(books_df),
        "unique_authors": int(books_df['Book-Author'].nunique()),
        "unique_publishers": int(books_df['Publisher'].nunique()),
        "year_range": year_range,
        "top_authors": top_authors,
        "top_publishers": top_publishers
    }

# Get top authors
@app.get("/authors/top")
async def get_top_authors(limit: int = Query(20, ge=1, le=100)):
    """Get top authors by book count"""
    if books_df is None or books_df.empty:
        raise HTTPException(status_code=404, detail="No books data available")
    
    author_counts = books_df['Book-Author'].value_counts().head(limit)
    
    return [
        {"author": author, "book_count": int(count)}
        for author, count in author_counts.items()
    ]

# Get top publishers
@app.get("/publishers/top")
async def get_top_publishers(limit: int = Query(20, ge=1, le=100)):
    """Get top publishers by book count"""
    if books_df is None or books_df.empty:
        raise HTTPException(status_code=404, detail="No books data available")
    
    publisher_counts = books_df['Publisher'].value_counts().head(limit)
    
    return [
        {"publisher": publisher, "book_count": int(count)}
        for publisher, count in publisher_counts.items()
    ]

# Get books by decade
@app.get("/books/by-decade/{decade}")
async def get_books_by_decade(
    decade: int = Field(..., ge=1000, le=2100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get books from a specific decade (e.g., 1990, 2000, 2010)"""
    if books_df is None or books_df.empty:
        return []
    
    # Convert year to numeric
    year_data = pd.to_numeric(books_df['Year-Of-Publication'], errors='coerce')
    
    # Filter by decade
    decade_books = books_df[
        (year_data >= decade) & (year_data < decade + 10)
    ]
    
    if decade_books.empty:
        return []
    
    start = skip
    end = skip + limit
    return decade_books.iloc[start:end].to_dict('records')

# Get publication year distribution
@app.get("/books/stats/year-distribution")
async def get_year_distribution(limit: int = Query(50, ge=1, le=100)):
    """Get publication year distribution"""
    if books_df is None or books_df.empty:
        raise HTTPException(status_code=404, detail="No books data available")
    
    year_data = pd.to_numeric(books_df['Year-Of-Publication'], errors='coerce')
    year_counts = year_data.value_counts().sort_index(ascending=False).head(limit)
    
    return {
        "distribution": {
            str(int(year)): int(count)
            for year, count in year_counts.items()
        }
    }

# Search books with multiple filters
@app.get("/books/advanced-search")
async def advanced_search(
    title: Optional[str] = Query(None, min_length=1),
    author: Optional[str] = Query(None, min_length=1),
    publisher: Optional[str] = Query(None, min_length=1),
    year: Optional[int] = Query(None, ge=1000, le=2100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Advanced search with multiple optional filters"""
    if books_df is None or books_df.empty:
        return []
    
    filtered_books = books_df.copy()
    
    if title:
        filtered_books = filtered_books[
            filtered_books['Book-Title'].str.contains(title, case=False, na=False)
        ]
    
    if author:
        filtered_books = filtered_books[
            filtered_books['Book-Author'].str.contains(author, case=False, na=False)
        ]
    
    if publisher:
        filtered_books = filtered_books[
            filtered_books['Publisher'].str.contains(publisher, case=False, na=False)
        ]
    
    if year:
        year_data = pd.to_numeric(filtered_books['Year-Of-Publication'], errors='coerce')
        filtered_books = filtered_books[year_data == year]
    
    if filtered_books.empty:
        return []
    
    start = skip
    end = skip + limit
    return filtered_books.iloc[start:end].to_dict('records')

# Get books without images
@app.get("/books/missing/images")
async def get_books_without_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get books that don't have image URLs"""
    if books_df is None or books_df.empty:
        return []
    
    books_without_images = books_df[
        books_df['Image-URL-S'].isna() | 
        books_df['Image-URL-M'].isna() | 
        books_df['Image-URL-L'].isna()
    ]
    
    start = skip
    end = skip + limit
    return books_without_images.iloc[start:end].to_dict('records')

# Get books without publisher
@app.get("/books/missing/publisher")
async def get_books_without_publisher(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get books that don't have publisher information"""
    if books_df is None or books_df.empty:
        return []
    
    books_without_publisher = books_df[books_df['Publisher'].isna()]
    
    start = skip
    end = skip + limit
    return books_without_publisher.iloc[start:end].to_dict('records')

# Get books without year
@app.get("/books/missing/year")
async def get_books_without_year(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get books that don't have publication year"""
    if books_df is None or books_df.empty:
        return []
    
    books_without_year = books_df[books_df['Year-Of-Publication'].isna()]
    
    start = skip
    end = skip + limit
    return books_without_year.iloc[start:end].to_dict('records')

# Get unique authors list
@app.get("/authors/list")
async def get_authors_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get list of unique authors"""
    if books_df is None or books_df.empty:
        return []
    
    authors = sorted(books_df['Book-Author'].dropna().unique())
    
    start = skip
    end = skip + limit
    return {"authors": authors[start:end], "total": len(authors)}

# Get unique publishers list
@app.get("/publishers/list")
async def get_publishers_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get list of unique publishers"""
    if books_df is None or books_df.empty:
        return []
    
    publishers = sorted(books_df['Publisher'].dropna().unique())
    
    start = skip
    end = skip + limit
    return {"publishers": publishers[start:end], "total": len(publishers)}

# Random books
@app.get("/books/random")
async def get_random_books(count: int = Query(10, ge=1, le=100)):
    """Get random books"""
    if books_df is None or books_df.empty:
        return []
    
    random_books = books_df.sample(n=min(count, len(books_df)))
    return random_books.to_dict('records')

# Create new book
@app.post("/books", status_code=201)
async def create_book(book: BookCreate):
    """Create a new book (in-memory only, not persisted to CSV)"""
    global books_df
    
    if books_df is None:
        raise HTTPException(status_code=500, detail="Books data not loaded")
    
    # Check if book already exists
    if book.isbn in books_df['ISBN'].values:
        raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    
    # Add new book to dataframe (in-memory only)
    new_row = pd.DataFrame([{
        'ISBN': book.isbn,
        'Book-Title': book.title,
        'Book-Author': book.author,
        'Year-Of-Publication': book.year,
        'Publisher': book.publisher,
        'Image-URL-S': book.image_url_s,
        'Image-URL-M': book.image_url_m,
        'Image-URL-L': book.image_url_l
    }])
    
    books_df = pd.concat([books_df, new_row], ignore_index=True)
    
    return {
        "message": "Book created successfully",
        "book": {
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author
        }
    }

# Update book
@app.put("/books/{isbn}")
async def update_book(isbn: str, book_update: BookUpdate):
    """Update an existing book (in-memory only)"""
    global books_df
    
    if books_df is None:
        raise HTTPException(status_code=500, detail="Books data not loaded")
    
    # Find the book
    mask = books_df['ISBN'] == isbn
    
    if not books_df[mask].any().any():
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update the book
    if book_update.title is not None:
        books_df.loc[mask, 'Book-Title'] = book_update.title
    
    if book_update.author is not None:
        books_df.loc[mask, 'Book-Author'] = book_update.author
    
    if book_update.year is not None:
        books_df.loc[mask, 'Year-Of-Publication'] = book_update.year
    
    if book_update.publisher is not None:
        books_df.loc[mask, 'Publisher'] = book_update.publisher
    
    if book_update.image_url_s is not None:
        books_df.loc[mask, 'Image-URL-S'] = book_update.image_url_s
    
    if book_update.image_url_m is not None:
        books_df.loc[mask, 'Image-URL-M'] = book_update.image_url_m
    
    if book_update.image_url_l is not None:
        books_df.loc[mask, 'Image-URL-L'] = book_update.image_url_l
    
    updated_book = books_df[mask].iloc[0].to_dict()
    
    return {
        "message": "Book updated successfully",
        "book": updated_book
    }

# Delete book
@app.delete("/books/{isbn}")
async def delete_book(isbn: str):
    """Delete a book (in-memory only)"""
    global books_df
    
    if books_df is None:
        raise HTTPException(status_code=500, detail="Books data not loaded")
    
    # Find the book
    mask = books_df['ISBN'] == isbn
    
    if not books_df[mask].any().any():
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Delete the book
    books_df = books_df[~mask]
    
    return {"message": "Book deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
    