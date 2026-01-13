"""Initialize database tables."""

from app.db.session import engine
from app.db.base import SQLModel

if __name__ == "__main__":
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✓ Database initialized successfully!")