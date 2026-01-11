"""Database session management."""

from sqlmodel import Session, create_engine
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True  # Verify connections before using them
)


def get_session():
    """Dependency that provides a database session."""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize database tables."""
    from app.db.base import SQLModel
    SQLModel.metadata.create_all(engine)