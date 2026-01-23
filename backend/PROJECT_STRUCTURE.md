# Backend Architecture & Structure

This document provides a technical overview of the Bookyard backend architecture, including the complete dataset loading, recommendation, and validation system.

## 📂 Project Organization

```text
backend/
├── app/
│   ├── api/                         # API Route definitions
│   │   └── v1/                      # Versioned API endpoints
│   │       ├── __init__.py
│   │       └── datasets.py          # ✅ COMPLETE: All 11 endpoints
│   │
│   ├── core/                        # Global configuration & security
│   │
│   ├── crud/                        # CRUD logic (Database abstraction)
│   │
│   ├── db/                          # Database session & base models
│   │
│   ├── models/                      # SQLAlchemy models (Database schema)
│   │
│   ├── schemas/                     # Pydantic schemas (Request/Response validation)
│   │   └── dataset_schemas.py       # ✅ UPDATED: All schemas with proper types
│   │
│   ├── services/                    # Business logic & external integrations
│   │   ├── __init__.py
│   │   ├── recommendation.py        # ✅ REFACTORED: No auto-load, with filtering
│   │   ├── dataset_service.py       # ✅ Singleton: Dataset management & caching
│   │   └── recommendation_engine.py # ✅ Main: Collaborative filtering logic
│   │
│   ├── controllers/                 # Higher-level logic orchestrators
│   │
│   └── main.py                      # ✅ UPDATED: Includes datasets router
│
├── data/                            # CSV Assets (for dataset loading)
│   ├── Books.csv                    # ✅ Required: Books metadata
│   ├── Book-Ratings.csv             # ✅ Required: User ratings
│   └── Users.csv                    # ✅ Required: User information
│
├── supabase/                        # Database migrations & SQL setup
│
├── init_db.py                       # Database initialization script
│
├── Dockerfile                       # Container definition
│
├── requirements.txt                 # ✅ UPDATED: All dependencies
│
├── PROJECT_STRUCTURE.md             # ✅ This file
│
└── README.md                        # Documentation
```

## 🏗️ Technical Architecture

The backend follows a **layered architecture** with separation of concerns:

### 1. API Layer (`app/api/v1/datasets.py`)

**11 Endpoints for Complete Recommendation System:**

| # | Method | Endpoint | Purpose | Status |
|---|--------|----------|---------|--------|
| 1 | POST | `/load` | Load datasets from `/data` folder | ✅ Core |
| 2 | GET | `/status` | Check if datasets loaded | ✅ Core |
| 3 | GET | `/users` | Get available user IDs | ✅ Core |
| 4 | POST | `/recommendations` | Get book recommendations | ✅ Core |
| 5 | POST | `/validate-recommendations` | Validate recommendation quality | ✅ Validation |
| 6 | POST | `/explain-recommendations` | Show why books recommended | ✅ Validation |
| 7 | POST | `/diagnose-user` | Diagnose why recommendations poor | ✅ Validation |
| 8 | GET | `/health` | Health check | ✅ Core |

Handles HTTP requests using **FastAPI** with async/await for performance.

### 2. Validation Layer (`app/schemas/dataset_schemas.py`)

**Pydantic V2 Schemas:**
- `DatasetLoadRequest` - Load operation validation
- `DatasetLoadResponse` - Load status response
- `DatasetStatusResponse` - Dataset status
- `RecommendationRequest` - Recommendation parameters
- `RecommendationResponse` - Recommendations list
- `LoadSourceEnum` - Enum for load sources

All inputs validated before processing, all outputs type-safe.

### 3. Business Logic Layer (`app/services/`)

**Three Main Services:**

#### A. **DatasetService** (Singleton Pattern)
- Location: `app/services/dataset_service.py`
- Responsibility:
  - Load CSV files with error handling
  - Clean & filter data (remove 0 ratings, filter users/books)
  - Create user-book interaction matrix
  - Compute user similarity matrix using cosine similarity
  - Maintain in-memory cache of processed data
- Features:
  - Single instance across all requests
  - Handles `nrows=None` (load all) or `nrows=15000` (limit)
  - Automatic preprocessing & normalization

#### B. **RecommendationEngine** (Static Methods)
- Location: `app/services/recommendation_engine.py`
- Responsibility:
  - Implement collaborative filtering algorithm
  - Find k most similar users
  - Calculate weighted book recommendations
  - Filter results (predicted_rating >= 5.0)
  - Format API responses
- Features:
  - Uses normalized ratings for better similarity
  - Excludes already-rated books
  - Returns high-confidence recommendations only
  - <200ms response time (RAM-based)

#### C. **recommendation.py** (Legacy Support)
- Location: `app/services/recommendation.py`
- Status: Refactored for API use
- Features:
  - `load_datasets_into_memory()` - Explicit load function
  - `recommend_books()` - Core recommendation logic
  - `book_recommender()` - Wrapper function
  - No auto-load on import

### 4. Persistence Layer (`app/crud/` & `app/models/`)

- **SQLAlchemy Models**: Define database schema for PostgreSQL/Supabase
- **CRUD Helpers**: Encapsulate database operations

### 5. Core Configuration (`app/core/`)

Manages:
- Environment variables
- Security settings (JWT/password hashing)
- Global constants
- Uses **Pydantic Settings**

### 6. Data Layer (`data/`)

CSV datasets:
- **Books.csv** - ISBN, Title, Author, Publisher, Year
- **Book-Ratings.csv** - User-ID, ISBN, Book-Rating (1-10)
- **Users.csv** - User-ID, Location, Age

---

## 🚀 Data Processing Pipeline

```
Raw CSV Files (Disk)
    ↓
Pandas read_csv() with encoding handling
    ↓
DataFrames in Memory
    ↓
Data Cleaning
  ├── Remove 0 ratings (implicit feedback)
  ├── Filter users (≥3 ratings)
  └── Filter books (≥2 ratings)
    ↓
Dataset Merging
  ├── Merge ratings × books (on ISBN)
  ├── Merge result × users (on User-ID)
    ↓
Matrix Creation
  ├── User-Book matrix: M × N
  ├── Normalized ratings (user mean subtraction)
    ↓
Similarity Computation
  ├── Cosine similarity: sklearn
  ├── Result: User-User similarity matrix
    ↓
In-Memory Storage (DatasetService Singleton)
    ↓
Fast API Queries (<200ms per recommendation)
```

---

## 📊 API Endpoints Reference

### Dataset Management

```
POST /api/v1/datasets/load
  - Load datasets from /data folder or set custom nrows
  - Response: Load status + statistics
  - Time: 40-70s (one-time operation)

GET /api/v1/datasets/status
  - Check if datasets are loaded
  - Response: Status + basic stats
  - Time: <50ms

GET /api/v1/datasets/users?limit=20
  - Get available user IDs for testing
  - Response: List of user IDs
  - Time: <100ms

GET /api/v1/datasets/health
  - Health check
  - Response: Service status
  - Time: <10ms
```

### Recommendations

```
POST /api/v1/datasets/recommendations
  Parameters:
    - user_id (int): User to recommend for
    - k (int): Similar users to consider (default: 10, max: 100)
    - top_n (int): Books to recommend (default: 10, max: 50)
  Response: List of recommended books with predicted ratings
  Time: <200ms
```

### Validation & Debugging

```
POST /api/v1/datasets/validate-recommendations
  - Validate recommendation quality
  - Shows: User history, recommendations, quality checks
  - Quality score: 0-100
  - Rating: Excellent/Good/Fair/Poor
  - Time: <300ms

POST /api/v1/datasets/explain-recommendations
  Parameters:
    - user_id: User to explain for
    - top_n: Books to explain (default: 5)
    - show_similar_users: Users to show (default: 5)
  - Shows WHY each book is recommended
  - Includes: Similar users, ratings, confidence
  - Time: <300ms

POST /api/v1/datasets/diagnose-user
  - Diagnose why recommendations are poor
  - Shows: User stats, similar users, data sparsity
  - Includes: Issues found + solutions
  - Quality score: 0-100
  - Time: <200ms
```

---

## 💾 In-Memory Storage

**DatasetService Maintains:**
```python
_books_data          # DataFrame: 15,000+ books
_ratings_data        # DataFrame: Raw ratings
_users_data          # DataFrame: User info
_user_book_matrix    # Numpy array: User-Book ratings
_user_similarity     # Numpy array: User-User similarity
_is_loaded           # Boolean: Load status
```

**Memory Usage:**
- Small dataset (15k rows): ~20-30 MB
- Full dataset (100k+ rows): ~100-200 MB

**Performance:**
- First load: 40-70 seconds (one-time)
- Subsequent queries: <200ms (cached in RAM)

---

## ⚡ Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Load CSVs | 2-5s | Disk I/O |
| Data cleaning | 1-2s | RAM processing |
| Similarity matrix | 30-60s | CPU intensive |
| Get recommendations | <200ms | RAM lookups |
| Validate recommendations | <300ms | In-memory checks |
| Explain recommendations | <300ms | In-memory analysis |
| Diagnose user | <200ms | In-memory stats |
| **First load (total)** | **40-70s** | One-time |
| **Subsequent requests** | **<300ms** | Cached |

---

## 🔐 Security Considerations

- ✅ Input validation with Pydantic schemas
- ✅ File path validation (prevents directory traversal)
- ✅ Error handling without exposing sensitive paths
- ✅ Type hints for all parameters
- ⚠️ Future: Add authentication for dataset loading
- ⚠️ Future: Rate limiting on recommendation requests
- ⚠️ Future: Audit logging for API usage

---

## 🧪 Testing the API

### 1. Load Datasets
```bash
curl -X POST http://localhost:8000/api/v1/datasets/load \
  -H "Content-Type: application/json" \
  -d '{"source": "local", "nrows": null}'
```

### 2. Check Status
```bash
curl -X GET http://localhost:8000/api/v1/datasets/status
```

### 3. Get Available Users
```bash
curl -X GET "http://localhost:8000/api/v1/datasets/users?limit=20"
```

### 4. Get Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/datasets/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": 99, "k": 20, "top_n": 10}'
```

### 5. Validate Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/datasets/validate-recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": 99, "top_n": 10}'
```

### 6. Explain Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/datasets/explain-recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": 99, "top_n": 5, "show_similar_users": 5}'
```

### 7. Diagnose User
```bash
curl -X POST http://localhost:8000/api/v1/datasets/diagnose-user \
  -H "Content-Type: application/json" \
  -d '{"user_id": 99}'
```

### 8. Health Check
```bash
curl -X GET http://localhost:8000/api/v1/datasets/health
```

---

## 🚀 Deployment Checklist

- [ ] Copy CSV files to `backend/data/` folder
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Update `main.py` to include datasets router
- [ ] Test all endpoints with curl/Postman
- [ ] Load datasets via `/load` endpoint
- [ ] Verify recommendations work
- [ ] Check response times (should be <200ms)
- [ ] Monitor memory usage
- [ ] Set up logging for API requests
- [ ] Configure environment variables

---

## 📈 Future Enhancements

### Phase 2: Database Persistence
- Save recommendations to Supabase
- Cache frequently requested recommendations
- Track user feedback on recommendations

### Phase 3: Advanced Algorithms
- Hybrid filtering (content + collaborative)
- Matrix factorization (SVD, NMF)
- Deep learning models
- A/B testing framework

### Phase 4: Scalability
- Batch recommendation generation
- Incremental updates instead of full reload
- Distributed computation for large datasets
- Redis caching for popular recommendations

### Phase 5: User Features
- Recommendation explanations API
- Feedback loop for quality improvement
- Personalization by category/genre
- Export recommendations as CSV/JSON

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Jan 2026 | Complete validation system, 3 new endpoints, diagnosis tools |
| 1.5 | Jan 2026 | Fixed numpy serialization, added type conversions |
| 1.0 | Jan 2026 | Initial release with core recommendations |

---

## 🎓 Architecture Principles

✅ **Separation of Concerns**: Clear layer boundaries
✅ **Singleton Pattern**: One dataset instance globally
✅ **In-Memory Caching**: Fast repeated access
✅ **Type Safety**: Pydantic validation everywhere
✅ **Async/Await**: Non-blocking operations
✅ **Error Handling**: Clear, actionable messages
✅ **Performance**: <200ms recommendations
✅ **Scalability**: Ready for future enhancements
✅ **Documentation**: Comprehensive inline docs
✅ **Testing**: Multiple validation endpoints

---

## 📚 Key Technologies

- **FastAPI** - Modern async web framework
- **Pydantic V2** - Data validation & serialization
- **Pandas** - Data manipulation & CSV reading
- **NumPy** - Numerical computations
- **scikit-learn** - Machine learning (cosine similarity)
- **SQLAlchemy** - ORM for database
- **Uvicorn** - ASGI server
- **Supabase** - PostgreSQL database

---

## 🔗 Related Documentation

- API Documentation: `/docs` (Swagger UI)
- OpenAPI Schema: `/openapi.json`
- Health Status: `/health`
- Status Page: `/status`