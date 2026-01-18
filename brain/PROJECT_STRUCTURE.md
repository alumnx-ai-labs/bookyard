# Backend Project Structure

## Directory Organization

```
backend/
├── app/
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # FastAPI app initialization & main routes
│   ├── models.py                      # Pydantic models
│   ├── database.py                    # Database logic & in-memory storage
│   └── controllers/
│       ├── __init__.py                # Controllers package
│       └── books_controller.py        # Books API endpoints (router)
├── requirements.txt                   # Python dependencies
└── .env.example                       # Environment variables template
```

## Module Responsibilities

### `main.py`
- FastAPI application initialization
- Lifespan event handlers (startup/shutdown)
- Root and health check endpoints
- Router registration

**Key components:**
- Lifespan context manager for application lifecycle
- `app = FastAPI(...)` initialization
- Health check and root endpoints

### `models.py`
- All Pydantic models for request/response validation
- `HealthResponse` - Health check response
- `Message` - Generic message response
- `BookBase` - Base book fields
- `BookCreate` - Book creation schema
- `BookUpdate` - Book update schema
- `Book` - Complete book model with ID

### `database.py`
- In-memory database storage
- Helper functions for CRUD operations:
  - `create_book(book)` - Create a new book
  - `get_all_books(skip, limit)` - Get paginated books
  - `get_book_by_id(book_id)` - Get specific book
  - `update_book(book_id, book_update)` - Update book
  - `delete_book(book_id)` - Delete book
  - `book_exists(book_id)` - Check if book exists

### `controllers/books_controller.py`
- FastAPI APIRouter for books endpoints
- Route handlers for all CRUD operations
- HTTP error handling (404, validation errors)
- Request/response logging

## Endpoint Routing

All endpoints are registered using `app.include_router(books_router)`:

```
POST   /api/books           - Create book
GET    /api/books           - List books (paginated)
GET    /api/books/{book_id} - Get specific book
PUT    /api/books/{book_id} - Update book
DELETE /api/books/{book_id} - Delete book
```

## Design Patterns

### Separation of Concerns
- **Models**: Data validation
- **Database**: Data storage and retrieval logic
- **Controllers**: HTTP request/response handling
- **Main**: Application initialization

### APIRouter Pattern
- Books controller uses FastAPI's `APIRouter`
- Enables modular, reusable route definitions
- Easy to add new controllers (auth, authors, etc.)

### Database Abstraction
- Database functions are separate from API handlers
- Easy to swap in-memory storage for a real database
- Database functions return Pydantic models

## Adding New Features

### Adding a New Controller (e.g., Authors API)

1. **Create `controllers/authors_controller.py`:**
```python
from fastapi import APIRouter
from app.models import Author
from app import database

router = APIRouter(prefix="/api/authors", tags=["authors"])

@router.get("", response_model=list[Author])
async def list_authors():
    return database.get_all_authors()
```

2. **Update `main.py`:**
```python
from controllers.authors_controller import router as authors_router
app.include_router(authors_router)
```

### Adding New Models

1. **Add to `models.py`:**
```python
class Author(BaseModel):
    id: int
    name: str
    ...
```

2. **Use in controllers** without circular imports

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

Visit `http://localhost:8000/docs` for Swagger UI to test all endpoints.

## Future Enhancements

- Replace in-memory database with SQLAlchemy + PostgreSQL
- Add authentication/authorization controller
- Add request validation middleware
- Add error handling middleware
- Create separate routes for different API versions
