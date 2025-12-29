from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CategoryCreate(BaseModel):
    """
    Schema zum Erstellen oder Aktualisieren einer Kategorie.
    """
    name: str = Field(
        ...,
        description="Name der Kategorie (z. B. Food, Rent, Salary)",
    )

    type: str = Field(
        ...,
        pattern="^(expense|income)$",
        description="Typ der Kategorie ('expense' oder 'income')",
    )

    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
    )


class CategoryRead(CategoryCreate):
    """
    Schema zum Zurückgeben einer Kategorie.
    """
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
