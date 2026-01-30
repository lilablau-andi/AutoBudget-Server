# Das Budget Schema gibt an wie Budgets erstellt und gelesen werden
# Autor: Andrej Bobb

from pydantic import BaseModel
from typing import Optional
from app.schemas.category import CategoryRead

# Schema zur Erstellung eines Budgets
class BudgetCreate(BaseModel):
    category_id: int
    amount: float
    period: str = "monthly"

# Schema um Budgets zu lesen
class BudgetRead(BaseModel):
    id: int
    category: CategoryRead
    amount: float
    period: str
    
    # Auszurechnende Felder
    spent: float
    remaining: float
    percentage: float

    class Config:
        from_attributes = True
