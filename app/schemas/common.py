# Das common schema ist eine allgemeine Sammlung um wiederkehrende Typen zu sammeln.
# Das hat hier gar nicht mal so viel Anwendung, ist aber für die Skalierbarkeit gut, 
# schonmal aufgesetzt zu sein.
# Autor: Andrej Bobb

from pydantic import BaseModel
from typing import Generic, TypeVar, List
from enum import Enum

# Standardschema für Transaktionstypen
class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"


# Standardschema für Seitenschemas. Das brauchen wir bei der Paginierung, um nicht alle Expenses 
# auf einen Schlag zu laden.
T = TypeVar("T")

class PaginationMeta(BaseModel):
    total_count: int
    total_pages: int
    page: int
    page_size: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta
