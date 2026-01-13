
import os
import sys
from uuid import uuid4

# Set SQLite DB 
os.environ["DATABASE_URL"] = "sqlite://"

# Add current directory to path
sys.path.append(os.getcwd())

from sqlmodel import Session, SQLModel, create_engine
from app.api.v1.endpoints.books import create_book
from app.schemas.book import BookCreate, BookResponse
from app.models.book import Book
from app.db import session as db_session

# Re-create engine
db_session.engine = create_engine("sqlite://", echo=False, connect_args={"check_same_thread": False})
engine = db_session.engine

def test_creation_flow():
    print("Initializing DB...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as db:
        print("Preparing Input Data...")
        # Data from user screenshot
        book_in = BookCreate(
            title="python",
            author="naga",
            published_year=2024,
            pages=185,
            description="best for fast learners"
        )
        
        user_id = uuid4()
        print(f"User ID: {user_id}")
        
        try:
            print("Calling create_book()...")
            # We call the function directly, bypassing FastAPI dependency injection mechanism
            # but passing valid arguments.
            result = create_book(book_in=book_in, db=db, current_user_id=user_id)
            print(f"✓ Success! Created Book ID: {result.id}")
            print(f"Owner ID: {result.owner_id}")
            
            print("Validating Response Model...")
            response = BookResponse.model_validate(result)
            print("✓ Response Model Validated")
            
        except Exception as e:
            print(f"✗ FAILED: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_creation_flow()
