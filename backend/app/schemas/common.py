"""Common Pydantic schemas."""

from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class Message(BaseModel):
    """Generic message response."""
    message: str


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response."""
    items: List[DataT]
    total: int
    skip: int
    limit: int