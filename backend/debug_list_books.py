
import os
import sys
from typing import List

# Set SQLite DB 
os.environ["DATABASE_URL"] = "sqlite://"

# Add current directory to path
sys.path.append(os.getcwd())

from sqlmodel import Session, SQLModel, create_engine
from app.crud.crud_book import crud_book
from app.schemas.book import BookResponse
from app.models.book import Book, BookCreate
from app.db import session as db_session

# Setup DB
db_session.engine = create_engine("sqlite://", echo=False, connect_args={"check_same_thread": False})
engine = db_session.engine

def debug_serialization():
    print("Setting up DB...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as db:
        print("Creating test book...")
        book_in = BookCreate(title="Test", author="Me", published_year=2023, pages=100)
        # Force string UUID
        owner_id = "00000000-0000-0000-0000-000000000000"
        book = crud_book.create(db, obj_in=book_in, owner_id=owner_id)
        
        print("Fetching books...")
        books = crud_book.get_multi_with_filters(db)
        print(f"Found {len(books)} books.")
        
        print("Attempting Pydantic Validation...")
        try:
            for b in books:
                print(f"Validating book {b.id}...")
                resp = BookResponse.model_validate(b)
                print("✓ Validated")
        except Exception as e:
            print(f"✗ Validation Failed: {e}")

if __name__ == "__main__":
    debug_serialization()
