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


class CategoryUpdate(BaseModel):
    """
    Schema zum Aktualisieren einer Kategorie. Alle Felder sind optional.
    """
    name: str | None = Field(
        None,
        description="Name der Kategorie (z. B. Food, Rent, Salary)",
    )

    type: str | None = Field(
        None,
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
