
import os
import sys

# Set SQLite DB for testing
os.environ["DATABASE_URL"] = "sqlite://"

# Add current directory to path
sys.path.append(os.getcwd())

from sqlmodel import Session, SQLModel, create_engine
from app.models.book import Book
from app.crud.crud_book import crud_book
from app.schemas.book import BookCreate

# Re-create engine for SQLite
from app.db import session as db_session
db_session.engine = create_engine("sqlite://", echo=False, connect_args={"check_same_thread": False})
engine = db_session.engine

def setup_db():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)

def reproduce_issue():
    setup_db()
    
    with Session(engine) as db:
        print("\nTesting Book Creation...")
        book_in = BookCreate(
            title="Test Book", 
            author="Test Author",
            published_year=2023,
            pages=100
        )
        
        # Mimic strict logic of endpoint (hardcoded owner)
        default_owner_id = "00000000-0000-0000-0000-000000000000"
        
        try:
            print(f"Attempting to create book with owner_id={default_owner_id}...")
            book = crud_book.create(db, obj_in=book_in, owner_id=default_owner_id)
            print(f"✓ Book created: {book.id} - {book.title}")
            print(f"  Owner ID: {book.owner_id}")
        except Exception as e:
            print(f"✗ Failed to create book: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    reproduce_issue()
