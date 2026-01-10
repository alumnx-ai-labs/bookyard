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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    
    Yields:
        None
    """
    # Startup
    logger.info("Application startup")
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


# Routes
@app.get("/", response_model=Message)
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Bookyard API"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Status, timestamp, and API version
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
