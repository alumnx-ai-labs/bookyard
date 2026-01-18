"""
Database configuration and session management.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
# echo=True enables logging of SQL statements provided by SQLModel/SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)



def init_db():
    """
    Initialize the database by creating all tables defined in SQLModel meta.
    Includes simple retry logic for Docker startup race conditions.
    """
    import time
    from sqlalchemy.exc import OperationalError
    
    max_retries = 5
    retry_wait = 2
    
    for attempt in range(max_retries):
        try:
            SQLModel.metadata.create_all(engine)
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database not ready, retrying in {retry_wait}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_wait)
            else:
                print("Failed to connect to database after several attempts.")
                raise e



def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting a database session.
    Yields a Session object.
    
    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session
