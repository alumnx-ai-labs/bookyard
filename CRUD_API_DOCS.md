# Book CRUD API Documentation

## Overview

The Bookyard API provides full CRUD (Create, Read, Update, Delete) operations for managing books.

## Base URL

```
http://localhost:8000/api
```

## Book Object

```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0743273565",
  "description": "A classic American novel",
  "published_year": 1925,
  "pages": 180,
  "created_at": "2025-01-10T12:34:56.789123",
  "updated_at": "2025-01-10T12:34:56.789123"
}
```

## Endpoints

### 1. Create a Book
**POST** `/books`

Creates a new book in the database.

**Request Body:**
```json
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0743273565",
  "description": "A classic American novel",
  "published_year": 1925,
  "pages": 180
}
```

**Required Fields:**
- `title` (string, 1-200 characters)
- `author` (string, 1-100 characters)

**Optional Fields:**
- `isbn` (string, max 20 characters)
- `description` (string, max 1000 characters)
- `published_year` (integer, 1000-2100)
- `pages` (integer, >= 1)

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0743273565",
  "description": "A classic American novel",
  "published_year": 1925,
  "pages": 180,
  "created_at": "2025-01-10T12:34:56.789123",
  "updated_at": "2025-01-10T12:34:56.789123"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0743273565",
    "published_year": 1925,
    "pages": 180
  }'
```

---

### 2. List All Books
**GET** `/books`

Retrieve a paginated list of all books.

**Query Parameters:**
- `skip` (integer, default: 0) - Number of books to skip
- `limit` (integer, default: 10) - Maximum number of books to return

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0743273565",
    "description": "A classic American novel",
    "published_year": 1925,
    "pages": 180,
    "created_at": "2025-01-10T12:34:56.789123",
    "updated_at": "2025-01-10T12:34:56.789123"
  }
]
```

**Example cURL:**
```bash
# Get first 10 books
curl "http://localhost:8000/api/books"

# Get books with pagination
curl "http://localhost:8000/api/books?skip=0&limit=5"
```

---

### 3. Get a Specific Book
**GET** `/books/{book_id}`

Retrieve details of a specific book by ID.

**Path Parameters:**
- `book_id` (integer) - ID of the book

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0743273565",
  "description": "A classic American novel",
  "published_year": 1925,
  "pages": 180,
  "created_at": "2025-01-10T12:34:56.789123",
  "updated_at": "2025-01-10T12:34:56.789123"
}
```

**Error:** `404 Not Found`
```json
{
  "detail": "Book with id 999 not found"
}
```

**Example cURL:**
```bash
curl "http://localhost:8000/api/books/1"
```

---

### 4. Update a Book
**PUT** `/books/{book_id}`

Update one or more fields of an existing book. Only provided fields will be updated.

**Path Parameters:**
- `book_id` (integer) - ID of the book

**Request Body (all fields optional):**
```json
{
  "title": "The Great Gatsby - Revised",
  "published_year": 1926
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "The Great Gatsby - Revised",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0743273565",
  "description": "A classic American novel",
  "published_year": 1926,
  "pages": 180,
  "created_at": "2025-01-10T12:34:56.789123",
  "updated_at": "2025-01-10T13:45:00.123456"
}
```

**Error:** `404 Not Found`
```json
{
  "detail": "Book with id 999 not found"
}
```

**Example cURL:**
```bash
curl -X PUT "http://localhost:8000/api/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby - Revised",
    "published_year": 1926
  }'
```

---

### 5. Delete a Book
**DELETE** `/books/{book_id}`

Remove a book from the database.

**Path Parameters:**
- `book_id` (integer) - ID of the book

**Response:** `204 No Content`

**Error:** `404 Not Found`
```json
{
  "detail": "Book with id 999 not found"
}
```

**Example cURL:**
```bash
curl -X DELETE "http://localhost:8000/api/books/1"
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource successfully created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid request data |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Create a book
response = requests.post(
    f"{BASE_URL}/books",
    json={
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0451524935",
        "published_year": 1949,
        "pages": 328
    }
)
book_id = response.json()["id"]
print(f"Created book: {book_id}")

# Get all books
response = requests.get(f"{BASE_URL}/books")
print(f"Total books: {len(response.json())}")

# Get specific book
response = requests.get(f"{BASE_URL}/books/{book_id}")
print(f"Book: {response.json()}")

# Update book
response = requests.put(
    f"{BASE_URL}/books/{book_id}",
    json={"title": "1984 - New Edition"}
)
print(f"Updated: {response.json()['title']}")

# Delete book
response = requests.delete(f"{BASE_URL}/books/{book_id}")
print(f"Deleted: {response.status_code}")
```

## Testing with Swagger UI

Visit `http://localhost:8000/docs` to access the interactive Swagger UI where you can test all endpoints directly.

## Notes

- Currently uses in-memory database (data is lost on server restart)
- For production, integrate with a persistent database (PostgreSQL, MongoDB, etc.)
- Timestamps are in UTC format (ISO 8601)
- All string fields are validated for length and required format
- Pagination defaults to 10 items per page
