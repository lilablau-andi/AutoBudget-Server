from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginationMeta(BaseModel):
    total_count: int
    total_pages: int
    page: int
    page_size: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta
