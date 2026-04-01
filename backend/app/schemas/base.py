from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMetadata(BaseModel):
    total_elements: int
    total_pages: int
    page: int
    limit: int

class PaginationResponse(BaseModel, Generic[T]):
    status: int = 1000
    message: str = "OK"
    data: List[T]
    pagination: PaginationMetadata

class ResponseSchema(BaseModel, Generic[T]):
    status: int = 1000
    message: str = "OK"
    data: Optional[T] = None

    class Config:
        from_attributes = True