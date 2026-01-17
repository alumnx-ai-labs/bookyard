"""
FastAPI application with health check endpoint and Book CRUD APIs.
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI

# Ensure app module is importable
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

from app.models import HealthResponse, Message
from app.controllers.books_controller import router as books_router
from app.controllers.users_controller import router as users_router
from app.controllers.data_controller import router as data_router
from app.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    logger.info("Application startup")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        
    logger.info("Bookyard API is running")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")


# Initialize FastAPI app
app = FastAPI(
    title="Bookyard API",
    description="FastAPI application for Bookyard",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(books_router)
app.include_router(users_router)
app.include_router(data_router)


# Routes
@app.get("/", response_model=Message)
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Bookyard API"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    """
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
