# Bookyard API

A FastAPI-based application with health check endpoint and scalable architecture.

## Features

- ✅ FastAPI with async support
- ✅ Health check endpoint (`GET /health`)
- ✅ Pydantic models for request/response validation
- ✅ Environment configuration support
- ✅ Structured logging
- ✅ OpenAPI documentation (Swagger UI)

## Project Structure

```
bookyard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment variables template
└── README.md                   # This file
```

## Setup

### 1. Create a Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your custom settings
```

## Running the Application

### Development Mode (with hot reload)

```bash
cd backend/app
python main.py
```

Or directly with uvicorn from the backend directory:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Production Mode

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
- **Endpoint:** `GET /health`
- **Description:** Returns API status and timestamp
- **Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-01-10T12:34:56.789123",
    "version": "0.1.0"
  }
  ```

### Root
- **Endpoint:** `GET /`
- **Description:** Welcome message
- **Response:**
  ```json
  {
    "message": "Welcome to Bookyard API"
  }
  ```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

### Using Python requests

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())
```

## API Documentation

Once the server is running, visit:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

## Extending the Application

### Add a New Endpoint

Edit `app/main.py` and add:

```python
@app.get("/api/endpoint")
async def my_endpoint():
    """Your endpoint description."""
    return {"data": "your response"}
```

### Add Request/Response Models

Create models in `app/main.py` or separate files:

```python
class MyRequest(BaseModel):
    name: str
    value: int

class MyResponse(BaseModel):
    message: str
    processed: bool

@app.post("/api/process")
async def process_data(request: MyRequest) -> MyResponse:
    return {"message": f"Processing {request.name}", "processed": True}
```

## Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation using Python type hints
- **python-dotenv** - Environment variable management

## License

MIT
